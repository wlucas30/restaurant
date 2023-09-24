#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 09:38:27 2023

@author: wl
"""

from flask import Flask

# This sets the app name to the same name as this file
app = Flask(__name__)

# This determines which page must be requested to call main()
@app.route("/restaurant")
def main():
    return "Here are some details that you have received"

if __name__ == "__main__":
    app.run(host="localhost", port=8080)