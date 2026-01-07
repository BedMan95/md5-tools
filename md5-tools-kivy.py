import hashlib
import requests
import re
import asyncio
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.logger import Logger

Window.size = (420, 720)
Window.clearcolor = (0.96, 0.96, 0.98, 1)

async def cheap_md5_lookup(hash_value: str) -> str | None:
    hash_value = hash_value.strip().lower()
    if len(hash_value) != 32 or not all(c in '0123456789abcdef' for c in hash_value):
        return None

    sites = [
        f"http://www.nitrxgen.net/md5db/{hash_value}.txt",
        f"https://md5.gromweb.com/?md5={hash_value}",
        # Add more if you find working ones
    ]

    for url in sites:
        try:
            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=8,
                headers={"User-Agent": "Kivy-MD5-Tool/2026"}
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
                except:
                    pass

            # Last desperate attempt - look for plausible strings
            candidates = re.findall(r'[\w !@#$%^&*()_+\-=\[\]{}|;:,.<>?\'"\\\/]{2,60}', text)
            for cand in candidates:
                plain = cand.strip()
                if 1 <= len(plain) <= 60 and hashlib.md5(plain.encode('utf-8')).hexdigest() == hash_value:
                    return plain

        except Exception:
            continue

        await asyncio.sleep(1.4)

    return None


# ────────────────────────────────────────────────────────────────
#  Kivy UI
# ────────────────────────────────────────────────────────────────
class MD5ToolsApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crack_result_label = None
        self.hash_result_label = None

    def build(self):
        root = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        # Title
        title = Label(
            text='MD5 Tools',
            font_size=sp(32),
            bold=True,
            color=(0.3, 0.4, 0.9, 1),
            size_hint_y=None,
            height=dp(60)
        )
        root.add_widget(title)

        # Tabs
        tabs = TabbedPanel(do_default_tab=False, tab_width=dp(140), tab_height=dp(48))

        # ── Hash tab ───────────────────────────────────────────────
        hash_tab = TabbedPanelItem(text='Hash Text')
        hash_content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        hash_content.add_widget(Label(
            text='Enter text to hash',
            font_size=sp(18),
            size_hint_y=None,
            height=dp(36)
        ))

        self.text_input = TextInput(
            multiline=True,
            hint_text='Type or paste your text here...',
            size_hint_y=None,
            height=dp(140),
            font_size=sp(16),
            background_color=(0.98, 0.98, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        hash_content.add_widget(self.text_input)

        hash_content.add_widget(Label(
            text='MD5 Hash result:',
            font_size=sp(16),
            size_hint_y=None,
            height=dp(36)
        ))

        self.hash_result_label = Label(
            text='—',
            font_size=sp(18),
            halign='left',
            valign='middle',
            text_size=(None, None),
            markup=True,
            size_hint_y=None,
            height=dp(80),
            padding=[dp(12), dp(12)]
        )
        scroll_hash = ScrollView(size_hint=(1, None), height=dp(80))
        scroll_hash.add_widget(self.hash_result_label)
        hash_content.add_widget(scroll_hash)

        btn_row_hash = BoxLayout(orientation='horizontal', spacing=dp(16), size_hint_y=None, height=dp(52))
        btn_hash = Button(
            text='Generate MD5',
            background_color=(0.3, 0.4, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        btn_hash.bind(on_press=self.do_hash)
        btn_row_hash.add_widget(btn_hash)

        btn_clear_hash = Button(
            text='Clear',
            background_color=(0.55, 0.55, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        btn_clear_hash.bind(on_press=self.clear_hash)
        btn_row_hash.add_widget(btn_clear_hash)

        hash_content.add_widget(btn_row_hash)
        hash_tab.add_widget(hash_content)
        tabs.add_widget(hash_tab)

        crack_tab = TabbedPanelItem(text='Crack MD5')
        crack_content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))

        crack_content.add_widget(Label(
            text='Enter MD5 hash (32 hex chars)',
            font_size=sp(18),
            size_hint_y=None,
            height=dp(36)
        ))

        self.hash_input = TextInput(
            multiline=False,
            hint_text='e.g. d41d8cd98f00b204e9800998ecf8427e',
            font_size=sp(18),
            size_hint_y=None,
            height=dp(52),
            write_tab=False
        )
        self.hash_input.bind(text=self.force_lowercase_hex)
        crack_content.add_widget(self.hash_input)

        crack_content.add_widget(Label(
            text='Cracking result:',
            font_size=sp(16),
            size_hint_y=None,
            height=dp(36)
        ))

        self.crack_result_label = Label(
            text='Ready to crack...',
            font_size=sp(16),
            halign='left',
            valign='top',
            text_size=(None, None),
            markup=True,
            size_hint_y=None,
            height=dp(160),
            padding=[dp(12), dp(12)]
        )
        scroll_crack = ScrollView(size_hint=(1, None), height=dp(160))
        scroll_crack.add_widget(self.crack_result_label)
        crack_content.add_widget(scroll_crack)

        btn_row_crack = BoxLayout(orientation='horizontal', spacing=dp(16), size_hint_y=None, height=dp(52))
        btn_crack = Button(
            text='Search Plaintext',
            background_color=(0.2, 0.65, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        btn_crack.bind(on_press=self.start_crack)
        btn_row_crack.add_widget(btn_crack)

        btn_clear_crack = Button(
            text='Clear',
            background_color=(0.55, 0.55, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18)
        )
        btn_clear_crack.bind(on_press=self.clear_crack)
        btn_row_crack.add_widget(btn_clear_crack)

        crack_content.add_widget(btn_row_crack)
        crack_tab.add_widget(crack_content)
        tabs.add_widget(crack_tab)

        root.add_widget(tabs)

        # Footer note
        footer = Label(
            text='Many online MD5 services are dead/unreliable in 2026',
            font_size=sp(12),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(footer)

        return root

    def force_lowercase_hex(self, instance, value):
        filtered = ''.join(c for c in value.lower() if c in '0123456789abcdef')
        if len(filtered) > 32:
            filtered = filtered[:32]

        # Prevent binding recursion
        if filtered != value:
            Clock.schedule_once(lambda dt: setattr(instance, 'text', filtered), -1)

    def do_hash(self, instance):
        txt = self.text_input.text.strip()
        if not txt:
            self.hash_result_label.text = '[color=ff4444]Please enter some text![/color]'
            return
        result = hashlib.md5(txt.encode('utf-8')).hexdigest()
        self.hash_result_label.text = f'[color=006600]{result}[/color]'

    def clear_hash(self, instance):
        self.text_input.text = ''
        self.hash_result_label.text = '—'

    def start_crack(self, instance):
        h = self.hash_input.text.strip().lower()
        if len(h) != 32 or not all(c in '0123456789abcdef' for c in h):
            self.crack_result_label.text = (
                '[color=ff4444][b]Invalid MD5 format![/b]\n'
                'Must be exactly 32 hexadecimal characters.[/color]'
            )
            return

        self.crack_result_label.text = '[color=3366ff]Searching... (may take a few seconds)[/color]'

        Clock.schedule_once(
            lambda dt: self._sync_crack_in_thread(h),
            0.1
        )


    def _sync_crack_in_thread(self, hash_value):
        try:
            result = asyncio.run(cheap_md5_lookup(hash_value))  # tetap pakai asyncio.run
        except Exception as e:
            result = None

        if result:
            text = (
                f'[b][color=006600]FOUND![/color][/b]\n\n'
                f'[b]Plaintext:[/b] {result}\n'
                f'[b]MD5:[/b] {hash_value}'
            )
        else:
            text = (
                '[color=cc7700][b]Not found[/b] in available public lookup services.[/color]\n\n'
                'Note (2026):\n'
                '• Most free online MD5 databases are dead or blocked\n'
                '• Try Hashcat + good wordlists / rules / masks\n'
                '• Use rainbow tables for common passwords'
            )

        self.crack_result_label.text = text

    def clear_crack(self, instance):
        self.hash_input.text = ''
        self.crack_result_label.text = 'Ready to crack...'


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    MD5ToolsApp().run()