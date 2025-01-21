from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.message import EmailMessage
import validators
from time import sleep
import re
from PIL import Image
import requests
import os
import streamlit as st
import base64

page_logo = Image.open('logo.png')
st.set_page_config(page_title="E-commerce Price Tracker", layout='wide', page_icon=page_logo)
new_title = '<p style="font-family:sans-serif; color:#cc8e3d; text-shadow: -1px -1px 0 #fff, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; font-weight:600; font-size: 42px; padding-left: 400px;">E-Commerce Price Tracker</p>'
st.markdown(new_title, unsafe_allow_html=True)
price_output = ''


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
            <style>
            .stApp {{
                background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
                background-size: cover
            }}
            </style>
            """,
        unsafe_allow_html=True
    )


add_bg_from_local("bg3.jpg")


class PriceTracker(ABC):
    """
    Base class for Price Trackers.
    """
    removals = re.compile(r"₹|,|[$]")

    def __init__(self, product_name: str, product_url: str, desired_price: int) -> None:
        """
        Constructor.
        """
        if not validators.url(product_url):
            raise Exception("Invalid URL!")

        self.product_url = product_url
        self.set_price = desired_price
        self.product_name = product_name
        self.price = None

    @abstractmethod
    def get_price(self):
        """
        Fetches the latest price of the product.
        """
        pass

    @staticmethod
    def email_alert(subject: str, body: str):
        """
        Sends mail for the given price.
        """
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = subject
        your_email = "aaddictor1@gmail.com"
        msg['to'] = your_email
        msg['from'] = your_email
        your_password = "phkbpyoerkcbzzkt"
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(your_email, your_password)
        server.send_message(msg)
        server.quit()
        print("Mail sent")

    @abstractmethod
    def write_to_file(self):
        """
        Write content to a text file.
        """
        pass

    def track_price(self):
        """
        Tracks price for a given product against the set price.
        """
        while True:
            self.get_price()
            if self.price == None:
                print("Unable to fetch the latest price!")
                os._exit(1)
            
            if self.set_price >= self.price:
                print("Price low for", self.product_name)
                st.write(f"<p style='color:white; font-size:28px; padding-left:360px;'>Price low for {self.product_name} ...</p>", unsafe_allow_html=True)
                self.write_to_file()
                self.email_alert(f"Price down for {self.product_name}", f"Dear sir,\nThe price for `{self.product_name}` is now {self.price} which is less than or equal to what you desired, {self.set_price}! Visit {self.product_url} for more info.")
                os._exit(0)

            else:
                self.write_to_file()
            sleep(60)


class FlipkartPriceTracker(PriceTracker):
    """
    Helps poor people by notifying them when the price of their favorite product on Flipkart is less than what they desired.
    """

    def get_price(self):
        """
        Fetches price for given product on Flipkart.
        """
        r = requests.get(self.product_url)
        soup = BeautifulSoup(r.content, "html5lib")
        price = soup.find("div", {"class": "_30jeq3 _16Jk6d"}).string
        price = re.sub(self.removals, "", price)
        self.price = int(price)

    def write_to_file(self):
        """
        Writes datetime and price to a file.
        """
        now = datetime.now().strftime("%d-%m-%y %H:%M %p")
        content = f"{now} --> Flipkart --> Rs:{self.price}/-\n"
        print(content)
        with open(f"Price History of {self.product_name}.txt", "a") as f:
            f.write(content)
        price_output = f'At {now}, Updated price value \u20B9{self.price}/-'
        st.write(f'<p style="color:white; font-size:28px; padding-left:360px;">{price_output}</p>', unsafe_allow_html=True)

    def run(self):
        self.track_price()


def check_internet():
    try:
        requests.get("https://google.com")
    
    except Exception as e:
        print("Make sure you're connected to the internet!")
        print(e)
        quit()


if __name__ == "__main__":
    check_internet()
    try:
        print("Welcome to the Ecommerce Price Tracker! A tool which you can use to track prices for a given product on Flipkart.\n")
        st.write("<p style='color:white; font-size:28px;'>Welcome to the Ecommerce Price Tracker! A tool which you can use to track prices for a given product on Flipkart ...</p>", unsafe_allow_html=True)
        product_name = st.text_input("", placeholder="Enter Product Name")
        product_url = st.text_input("", placeholder="Enter Product URL")
        desired_price = int(st.text_input("", placeholder="Enter Your Desired Price"))
        st.write("")
        st.write("")
        if st.button("Track Price"):
            st.write(f"<p style='color:orange; font-size:36px;'>Current Price of {product_name} in Flipkart", unsafe_allow_html=True)
            fkt = FlipkartPriceTracker(product_name, product_url, desired_price)
            fkt.run()

    except Exception as e:
        print("Some problem occurs ... ")
        print(e)
