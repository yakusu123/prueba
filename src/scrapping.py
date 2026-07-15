from datetime import datetime
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datos import guardar_datos_extraidos  # type: ignore[attr-defined]

options = Options()

# 1. Configuracion Opera
options.binary_location = r"C:\Users\Vic3n\AppData\Local\Programs\Opera GX\opera.exe"
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--remote-debugging-port=9222")
service = Service(ChromeDriverManager(driver_version="148.0.7778.265").install())

driver = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(driver, timeout=15)
driver.get("https://sandbox.oxylabs.io/products")

datos = []

for x in range(5):
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".product-card")))
    productos = driver.find_elements(By.CSS_SELECTOR, ".product-card.css-e8at8d.eag3qlw10")
    for producto in productos:
        href = producto.find_element(By.CSS_SELECTOR, "a.card-header.css-o171kl.eag3qlw2").get_attribute("href")
        id_producto = int(href.split("/")[-1])  # type: ignore[union-attr]
        titulo = producto.find_element(By.CSS_SELECTOR, ".title.css-7u5e79.eag3qlw7").text
        lista_categorias = producto.find_elements(By.CSS_SELECTOR, ".css-1pewyd6.eag3qlw8")
        categorias = ", ".join([cat.text for cat in lista_categorias])
        precio_texto = producto.find_element(By.CSS_SELECTOR, ".price-wrapper.css-li4v8k.eag3qlw4").text
        precio = float(precio_texto.replace("€", "").replace(",", ".").strip())
        datos.append(
            {
                "id_producto": id_producto,
                "titulo": titulo,
                "categorias": categorias,
                "precio": precio,
                "fecha": datetime.today().strftime("%d/%m/%Y"),
            }
        )
    try:
        boton = driver.find_element(By.CLASS_NAME, "next")
        boton.click()
        time.sleep(2)
    except Exception as e:
        print("No se encontró el botón de siguiente página o se acabaron las páginas.")
        break
driver.quit()
guardar_datos_extraidos(datos)