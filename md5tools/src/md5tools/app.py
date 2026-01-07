import hashlib
import requests
import re
import asyncio
from toga import App, Box, Label, TextInput, Button, OptionContainer, MainWindow
from toga.style import Pack


async def cheap_md5_lookup(hash_value: str) -> str | None:
    hash_value = hash_value.strip().lower()
    if len(hash_value) != 32 or not all(c in '0123456789abcdef' for c in hash_value):
        return None

    sites = [
        f"http://www.nitrxgen.net/md5db/{hash_value}.txt",
        f"https://md5.gromweb.com/?md5={hash_value}",
    ]

    for url in sites:
        try:
            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=8,
                headers={"User-Agent": "Toga-MD5-Tool/2026"}
            )
            text = response.text.strip()

            if not text or any(x in text.lower() for x in ["not found", "no match", "could not"]):
                continue

            if "nitrxgen" in url and len(text) < 120:
                return text

            if "gromweb" in url and "The MD5 hash" in text:
                try:
                    start = text.find('The MD5 hash') + 140
                    end = text.find('</p>', start)
                    segment = text[start:end].strip()
                    if '/?string=' in segment:
                        plain = segment.split('/?string=')[-1].split('"')[0]
                        return plain.replace("%20", " ").replace("+", " ")
                    else:
                        return segment.strip('"').strip("'")
                except Exception:
                    pass

            candidates = re.findall(r'[\w !@#$%^&*()_+\-=\[\]{}|;:,.<>?\'"\\\/]{2,60}', text)
            for cand in candidates:
                plain = cand.strip()
                if 1 <= len(plain) <= 60 and hashlib.md5(plain.encode('utf-8')).hexdigest() == hash_value:
                    return plain

        except Exception:
            continue

        await asyncio.sleep(1.4)

    return None


class MD5Tools(App):
    def startup(self):
        main_box = Box(style=Pack(direction="column", margin=10, background_color="#f5f6f9"))

        title = Label(
            "MD5 Tools",
            style=Pack(font_size=32, font_weight="bold", color="#4f46e5", text_align="center", margin=(20, 0, 10, 0))
        )
        main_box.add(title)

        tabs = OptionContainer(
            style=Pack(flex=1),
            content=[
                ("Hash Text", self.create_hash_tab()),
                ("Crack MD5", self.create_crack_tab()),
            ]
        )
        main_box.add(tabs)

        footer = Label(
            "Many online MD5 services are dead/unreliable in 2026",
            style=Pack(font_size=12, color="#9ca3af", text_align="center", margin=10)
        )
        main_box.add(footer)

        self.main_window = MainWindow(title=self.formal_name, size=(440, 740))
        self.main_window.content = main_box
        self.main_window.show()

    def create_hash_tab(self):
        content = Box(style=Pack(direction="column", margin=12, background_color="#ffffff"))

        content.add(Label("Enter text to hash", style=Pack(font_size=18, margin_bottom=8)))

        self.text_input = TextInput(
            placeholder="Type or paste your text here...",
            style=Pack(flex=1, font_size=16)
        )
        content.add(self.text_input)

        content.add(Label("MD5 Hash result:", style=Pack(font_size=16, margin=(10, 0, 0, 0))))

        self.hash_result_label = Label(
            "—",
            style=Pack(
                flex=1,
                font_size=18,
                color="#374151",
                margin=12,
                background_color="#f3f4f6",
                font_family="monospace",
                width=380,
                height=300,
                text_align="left"
            )
        )
        content.add(self.hash_result_label)

        btn_row = Box(style=Pack(direction="row", gap=16, margin_top=12))
        hash_btn = Button(
            "Generate MD5",
            on_press=self.do_hash,
            style=Pack(background_color="#4f46e5", color="white", padding=12, font_size=16)
        )
        clear_btn = Button(
            "Clear",
            on_press=self.clear_hash,
            style=Pack(background_color="#6b7280", color="white", padding=12, font_size=16)
        )
        btn_row.add(hash_btn)
        btn_row.add(clear_btn)
        content.add(btn_row)

        return content

    def create_crack_tab(self):
        content = Box(style=Pack(direction="column", margin=12, background_color="#ffffff"))

        content.add(Label("Enter MD5 hash (32 hex chars)", style=Pack(font_size=18, margin_bottom=8)))

        self.hash_input = TextInput(
            placeholder="e.g. d41d8cd98f00b204e9800998ecf8427e",
            style=Pack(font_size=18, font_family="monospace"),
            on_change=self.force_lowercase_hex
        )
        content.add(self.hash_input)

        content.add(Label("Cracking result:", style=Pack(font_size=16, margin=(10, 0, 0, 0))))

        self.crack_result_label = Label(
            "Ready to crack...",
            style=Pack(
                flex=1,
                font_size=16,
                margin=12,
                background_color="#f3f4f6",
                width=380,
                height=300,
                text_align="left"
            )
        )
        content.add(self.crack_result_label)

        btn_row = Box(style=Pack(direction="row", gap=16, margin_top=12))
        crack_btn = Button(
            "Search Plaintext",
            on_press=self.start_crack,
            style=Pack(background_color="#16a34a", color="white", padding=12, font_size=16)
        )
        clear_btn = Button(
            "Clear",
            on_press=self.clear_crack,
            style=Pack(background_color="#6b7280", color="white", padding=12, font_size=16)
        )
        btn_row.add(crack_btn)
        btn_row.add(clear_btn)
        content.add(btn_row)

        return content

    def force_lowercase_hex(self, widget):
        value = widget.value.lower()
        filtered = ''.join(c for c in value if c in '0123456789abcdef')
        if len(filtered) > 32:
            filtered = filtered[:32]
        if filtered != widget.value:
            widget.value = filtered

    def do_hash(self, widget):
        txt = self.text_input.value.strip()
        if not txt:
            self.hash_result_label.text = "Please enter some text!"
            return
        result = hashlib.md5(txt.encode('utf-8')).hexdigest()
        self.hash_result_label.text = result

    def clear_hash(self, widget):
        self.text_input.value = ""
        self.hash_result_label.text = "—"

    async def start_crack_async(self):
        h = self.hash_input.value.strip().lower()
        if len(h) != 32 or not all(c in '0123456789abcdef' for c in h):
            self.crack_result_label.text = "Invalid MD5 format!\nMust be exactly 32 hexadecimal characters."
            return

        self.crack_result_label.text = "Searching... (may take a few seconds)"

        result = await cheap_md5_lookup(h)

        if result:
            self.crack_result_label.text = f"FOUND!\n\nPlaintext: {result}\nMD5: {h}"
        else:
            self.crack_result_label.text = (
                "Not found in available public lookup services.\n\n"
                "Note (2026):\n"
                "• Most free online MD5 databases are dead or blocked\n"
                "• Try Hashcat + good wordlists / rules / masks\n"
                "• Use rainbow tables for common passwords"
            )

    def start_crack(self, widget):
        asyncio.create_task(self.start_crack_async())   # ← modern & clean

    def clear_crack(self, widget):
        self.hash_input.value = ""
        self.crack_result_label.text = "Ready to crack..."

    async def on_app_running(self, app):
        pass


def main():
    return MD5Tools("MD5 Tools", "org.example.md5tools")