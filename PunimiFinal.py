import json
from datetime import datetime
from pathlib import Path

# Ky projekt eshte nje sistem i thjeshte per menaxhimin e nje supermarketi.
# Programi punon ne terminal dhe perdor menu per produktet, stokun, shitjet,
# faturat dhe raportet.

# BASE tregon folderin ku ndodhet ky fajll Python.
# Kjo perdoret qe fajllat JSON te ruhen ne te njejtin folder me programin.
BASE = Path(__file__).resolve().parent

# Keto dy fajlla JSON ruajne te dhenat e programit.
# PRODUCTS_FILE ruan produktet, ndersa SALES_FILE ruan faturat/shitjet.
PRODUCTS_FILE = BASE / "supermarket_products.json"
SALES_FILE = BASE / "supermarket_sales.json"

# VAT eshte TVSH-ja 18%.
# LOW_STOCK perdoret per me gjet produktet qe kane stok te ulet.
VAT = 0.18
LOW_STOCK = 5

# Funksioni load lexon te dhenat nga nje fajll JSON.
# Nese fajlli nuk ekziston ose ka gabim, kthen liste bosh.
def load(path):
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

# Funksioni save ruan listen e produkteve ose shitjeve ne JSON.
# ensure_ascii=False lejon shkronja shqipe nese perdoren ne tekst.
def save(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# Kthen daten dhe oren aktuale, qe perdoret te produktet dhe faturat.
def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Printon nje vije ndarese per me e bere pamjen me te rregullt ne terminal.
def line():
    print("-" * 70)

# Ndal programin derisa perdoruesi te shtype ENTER.
def pause():
    input("\nShtyp ENTER per te vazhduar...")

# Merr tekst nga perdoruesi dhe nuk lejon input bosh.
def text(msg):
    while True:
        value = input(msg).strip()
        if value:
            return value
        print("Nuk lejohet bosh.")

# Merr numer nga perdoruesi.
# kind mund te jete float per cmim ose int per stok/sasi.
# minimum tregon vleren me te vogel qe lejohet.
def number(msg, kind=float, minimum=0):
    while True:
        try:
            value = kind(input(msg).strip())
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Shkruaj numer >= {minimum}.")

# Krijon ID automatike per produktin e ri.
# Nese nuk ka produkte, ID fillon nga 1001.
def next_id(products):
    return 1001 if not products else max(p["id"] for p in products) + 1

# Kerko produktin sipas ID-se.
# E kthen produktin nese gjendet, perndryshe kthen None.
def find(products, product_id):
    for product in products:
        if str(product["id"]) == str(product_id):
            return product
    return None

# Shfaq titujt e tabeles se produkteve.
def header():
    print(f"{'ID':<7}{'Emri':<20}{'Kategoria':<13}{'Cmimi':<9}{'Stoku':<7}Furnitori")
    line()

# Shfaq nje produkt ne nje rresht te tabeles.
def row(product):
    print(
        f"{product['id']:<7}{product['name']:<20}{product['category']:<13}"
        f"{product['price']:<9.2f}{product['stock']:<7}{product['supplier']}"
    )

# Shfaq listen e te gjitha produkteve.
def show_products(products):
    print("\nLISTA E PRODUKTEVE")
    line()
    if not products:
        print("Nuk ka produkte.")
        return
    header()
    for product in products:
        row(product)

# Shton produkt te ri.
# Produkti ruhet si dictionary me ID, emer, kategori, cmim, stok dhe furnitor.
def add_product(products):
    print("\nSHTO PRODUKT")
    product = {
        "id": next_id(products),
        "name": text("Emri: "),
        "category": text("Kategoria: "),
        "price": number("Cmimi: ", float, 0.01),
        "stock": number("Stoku: ", int, 0),
        "supplier": text("Furnitori: "),
        "created_at": now(),
    }
    products.append(product)
    save(PRODUCTS_FILE, products)
    print(f"Produkti u shtua me ID {product['id']}.")

# Perditeson nje produkt ekzistues.
# Perdoruesi mund te lere bosh fushat qe nuk deshiron t'i ndryshoje.
def update_product(products):
    print("\nPERDITESO PRODUKT")
    product = find(products, text("ID: "))
    if not product:
        print("Produkti nuk u gjet.")
        return
    print("Leri bosh ato qe nuk do t'i ndryshosh.")
    fields = [
        ("name", "Emri", str),
        ("category", "Kategoria", str),
        ("price", "Cmimi", float),
        ("stock", "Stoku", int),
        ("supplier", "Furnitori", str),
    ]
    for key, label, kind in fields:
        value = input(f"{label} ({product[key]}): ").strip()
        if not value:
            continue
        try:
            product[key] = kind(value)
            if key == "price" and product[key] <= 0:
                product[key] = 0.01
            if key == "stock" and product[key] < 0:
                product[key] = 0
        except ValueError:
            print(f"{label} nuk u ndryshua.")
    product["updated_at"] = now()
    save(PRODUCTS_FILE, products)
    print("Produkti u perditesua.")

# Fshin nje produkt, por vetem pasi perdoruesi e konfirmon me "po".
def delete_product(products):
    print("\nFSHI PRODUKT")
    product = find(products, text("ID: "))
    if not product:
        print("Produkti nuk u gjet.")
        return
    answer = input(f"A do ta fshish '{product['name']}'? (po/jo): ").lower()
    if answer == "po":
        products.remove(product)
        save(PRODUCTS_FILE, products)
        print("Produkti u fshi.")
    else:
        print("Fshirja u anulua.")

# Kerko produkt me ID ose me emer.
# Te kerkimi me emer perdoret keyword, pra mjafton nje pjese e emrit.
def search_product(products):
    print("\nKERKO PRODUKT")
    choice = input("1. Me ID\n2. Me emer\nZgjedh: ").strip()
    if choice == "1":
        product = find(products, text("ID: "))
        results = [product] if product else []
    elif choice == "2":
        keyword = text("Emri: ").lower()
        results = [p for p in products if keyword in p["name"].lower()]
    else:
        print("Zgjedhje e gabuar.")
        return
    if not results:
        print("Nuk u gjet produkt.")
        return
    header()
    for product in results:
        row(product)

# Shton sasi te re ne stokun e nje produkti.
def add_stock(products):
    print("\nSHTO STOK")
    product = find(products, text("ID: "))
    if not product:
        print("Produkti nuk u gjet.")
        return
    print(f"{product['name']} ka {product['stock']} cope.")
    product["stock"] += number("Shto sasi: ", int, 1)
    product["updated_at"] = now()
    save(PRODUCTS_FILE, products)
    print(f"Stoku i ri: {product['stock']}")

# Shton produkt ne shporte/fature.
# Para se te shtohet, kontrollohet a ekziston produkti dhe a ka stok te mjaftueshem.
def add_to_cart(products, cart):
    product = find(products, text("ID produkti: "))
    if not product:
        print("Produkti nuk u gjet.")
        return
    if product["stock"] <= 0:
        print("Produkti nuk ka stok.")
        return
    print(f"{product['name']} | {product['price']:.2f} EUR | stok {product['stock']}")
    qty = number("Sasia: ", int, 1)
    if qty > product["stock"]:
        print("Nuk ka mjaftueshem stok.")
        return
    cart.append({
        "product_id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "quantity": qty,
        "total": product["price"] * qty,
    })
    print("U shtua ne fature.")

# Llogarit nentotalin, TVSH-ne dhe totalin e fatures.
def cart_totals(cart):
    subtotal = sum(item["total"] for item in cart)
    return subtotal, subtotal * VAT, subtotal + subtotal * VAT

# Shfaq faturen aktuale para se te perfundohet shitja.
def show_cart(cart):
    print("\nFATURA AKTUALE")
    line()
    if not cart:
        print("Fatura eshte bosh.")
        return
    for item in cart:
        print(f"{item['name']:<22}{item['quantity']} x {item['price']:.2f} = {item['total']:.2f}")
    subtotal, vat, total = cart_totals(cart)
    line()
    print(f"Nentotali: {subtotal:.2f} EUR")
    print(f"TVSH: {vat:.2f} EUR")
    print(f"Totali: {total:.2f} EUR")

# Printon faturen perfundimtare ne ekran.
def print_invoice(invoice):
    print("\n" + "=" * 70)
    print("FATURA E SUPERMARKETIT")
    print("=" * 70)
    print(f"Nr: {invoice['invoice_id']} | Klienti: {invoice['customer']} | {invoice['date']}")
    line()
    for item in invoice["items"]:
        print(f"{item['name']:<22}{item['quantity']} x {item['price']:.2f} = {item['total']:.2f}")
    line()
    print(f"Nentotali: {invoice['subtotal']:.2f} EUR")
    print(f"TVSH {int(VAT * 100)}%: {invoice['vat']:.2f} EUR")
    print(f"TOTALI: {invoice['total']:.2f} EUR")
    print("=" * 70)

# Perfundon shitjen.
# Ketu krijohet fatura, ulet stoku i produkteve dhe ruhen te dhenat ne JSON.
def finish_sale(products, sales, cart):
    if not cart:
        print("Nuk ka produkte ne fature.")
        return False
    subtotal, vat, total = cart_totals(cart)
    invoice = {
        "invoice_id": len(sales) + 1,
        "customer": input("Klienti: ").strip() or "Klient",
        "date": now(),
        "items": cart,
        "subtotal": subtotal,
        "vat": vat,
        "total": total,
    }
    for item in cart:
        find(products, item["product_id"])["stock"] -= item["quantity"]
    sales.append(invoice)
    save(PRODUCTS_FILE, products)
    save(SALES_FILE, sales)
    print_invoice(invoice)
    return True

# Menaxhon procesin e shitjes.
# Krijon nje shporte bosh dhe lejon shtim produktesh, shfaqje fature ose anulim.
def make_sale(products, sales):
    cart = []
    while True:
        print("\n1. Shto produkt\n2. Shfaq faturen\n3. Perfundo shitjen\n4. Anulo")
        choice = input("Zgjedh: ").strip()
        if choice == "1":
            add_to_cart(products, cart)
        elif choice == "2":
            show_cart(cart)
        elif choice == "3" and finish_sale(products, sales, cart):
            break
        elif choice == "4":
            print("Shitja u anulua.")
            break
        else:
            print("Zgjedhje e gabuar.")

# Shfaq produktet qe kane stok me te vogel ose te barabarte me LOW_STOCK.
def low_stock(products):
    print("\nPRODUKTE ME STOK TE ULET")
    low = [p for p in products if p["stock"] <= LOW_STOCK]
    if not low:
        print("Nuk ka produkte me stok te ulet.")
        return
    header()
    for product in low:
        row(product)

# Raporti i shitjeve tregon numrin e faturave, produktet e shitura,
# TVSH-ne totale, te ardhurat dhe produktin me te shitur.
def sales_report(sales):
    print("\nRAPORT SHITJESH")
    line()
    if not sales:
        print("Ende nuk ka shitje.")
        return
    income = sum(s["total"] for s in sales)
    vat_total = sum(s["vat"] for s in sales)
    sold = sum(i["quantity"] for s in sales for i in s["items"])
    top_products = {}
    for sale in sales:
        for item in sale["items"]:
            top_products[item["name"]] = top_products.get(item["name"], 0) + item["quantity"]
    top = max(top_products.items(), key=lambda x: x[1])
    print(f"Fatura: {len(sales)}")
    print(f"Produkte te shitura: {sold}")
    print(f"TVSH totale: {vat_total:.2f} EUR")
    print(f"Te ardhura: {income:.2f} EUR")
    print(f"Me i shituri: {top[0]} ({top[1]} cope)")

# Shfaq 10 faturat e fundit nga historia e shitjeve.
def invoice_history(sales):
    print("\nHISTORIA E FATURAVE")
    if not sales:
        print("Ende nuk ka fatura.")
        return
    for sale in sales[-10:]:
        print(f"#{sale['invoice_id']} | {sale['customer']} | {sale['date']} | {sale['total']:.2f} EUR")

# Shton disa produkte demo per testim/prezantim.
def add_demo(products):
    demo = [
        ("Qumesht", "Bulmet", 1.20, 30, "Vita"),
        ("Buke", "Furre", 0.60, 50, "Furra"),
        ("Vaj", "Ushqimore", 2.40, 15, "AgroPlus"),
        ("Kafe", "Pije", 3.50, 12, "Aroma"),
        ("Uje 1.5L", "Pije", 0.45, 80, "BlueWater"),
        ("Molle", "Fruta", 0.90, 25, "Ferma"),
    ]
    for name, category, price, stock, supplier in demo:
        products.append({
            "id": next_id(products), "name": name, "category": category,
            "price": price, "stock": stock, "supplier": supplier, "created_at": now(),
        })
    save(PRODUCTS_FILE, products)
    print("Produktet demo u shtuan.")

# Menuja kryesore qe shfaqet ne terminal.
def menu():
    line()
    print("SUPERMARKET MANAGEMENT SYSTEM")
    line()
    print("1. Shfaq produktet")
    print("2. Shto produkt")
    print("3. Perditeso produkt")
    print("4. Fshi produkt")
    print("5. Kerko produkt")
    print("6. Shto stok")
    print("7. Bej shitje / fature")
    print("8. Produkte me stok te ulet")
    print("9. Raporti i shitjeve")
    print("10. Historia e faturave")
    print("11. Shto produkte demo")
    print("12. Dil")
    line()

# Funksioni kryesor i programit.
# Ketu lexohen produktet dhe shitjet nga JSON dhe lidhen opsionet e menus me funksionet.
def main():
    products = load(PRODUCTS_FILE)
    sales = load(SALES_FILE)
    actions = {
        "1": lambda: show_products(products), "2": lambda: add_product(products),
        "3": lambda: update_product(products), "4": lambda: delete_product(products),
        "5": lambda: search_product(products), "6": lambda: add_stock(products),
        "7": lambda: make_sale(products, sales), "8": lambda: low_stock(products),
        "9": lambda: sales_report(sales), "10": lambda: invoice_history(sales),
        "11": lambda: add_demo(products),
    }
    while True:
        menu()
        choice = input("Zgjedh opsionin: ").strip()
        if choice == "12":
            print("Programi u mbyll. Faleminderit!")
            break
        action = actions.get(choice)
        action() if action else print("Zgjedhje e gabuar.")
        pause()

# Kjo siguron qe programi te niset vetem kur fajlli ekzekutohet direkt.
if __name__ == "__main__":
    main()
