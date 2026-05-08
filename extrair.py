def ler_txt(caminho):
    encodings = ["utf-8", "iso-8859-1"]

    for enc in encodings:
        try:
            with open(caminho, "r", encoding=enc) as f:
                texto = f.read()

            print(f"[OK] Lido com: {enc}")
            return texto, enc

        except UnicodeDecodeError:
            continue

    raise Exception("Não foi possível ler o ficheiro.")

texto_bruto, encoding = ler_txt("exemplo.txt")

print(texto_bruto)
print("\nEncoding:", encoding)