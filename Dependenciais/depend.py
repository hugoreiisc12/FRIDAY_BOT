# Orientada a objetos com separação de responsabilidades

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import threading
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class WebDriverFactory:
    """Fábrica simples para criar um Chrome WebDriver usando webdriver-manager.

    Observação: o driver só é realmente inicializado quando `create_driver` é chamado.
    Em ambientes de teste sem GUI, não chame `create_driver()` sem mocks.
    """

    def __init__(self, headless: bool = True):
        self.headless = headless

    def create_driver(self):
        options = Options()
        if self.headless:
            # Chrome 109+ usa --headless=new
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

        # Import local para evitar custo no import do módulo
        from webdriver_manager.chrome import ChromeDriverManager

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        return driver

