import sqlite3  # SQLite database module
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image
from newspaper import Article
from transformers import pipeline  # Import transformers for sentiment analysis and fake news detection
import nltk
from urllib.parse import urlparse
import azure.cognitiveservices.speech as speechsdk  # Azure TTS


# Download nltk dependencies
nltk.download('punkt')

# Set screen size to mimic a phone size
Window.size = (400, 600)
# Azure Speech Service Key and Region (Replace with actual values)
AZURE_SPEECH_KEY = "A9Jwlb4mK7wFu9tEumTFnDE2W0vrQeEpciHfDFha2juGbckFCCmgJQQJ99BCACYeBjFXJ3w3AAAYACOG5Foz"  # Replace with your Azure key
AZURE_SPEECH_REGION = "eastus"  # Replace with your Azure region

# Database Initialization
def init_db():
    conn = sqlite3.connect('app_data.db')
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS article_history (
                        username TEXT,
                        title TEXT,
                        date TEXT,
                        summary TEXT,
                        sentiment_label TEXT,
                        sentiment_score REAL,
                        credibility TEXT,
                        FOREIGN KEY(username) REFERENCES users(username))''')

    conn.commit()
    conn.close()


class ArticleApp(MDApp):
    def build(self):
        init_db()  # Initialize the database
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.theme_style = "Dark"

        # Initialize sentiment analysis pipeline
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
        )

        # Initialize fake news detector (using a model from Hugging Face or any trained model)
        self.fake_news_detector = pipeline(
            "zero-shot-classification", model="facebook/bart-large-mnli"
        )

        # Create ScreenManager to manage screens
        self.screen_manager = MDScreenManager()

        # Add Login, Sign Up, and Article screens
        self.screen_manager.add_widget(self.build_login_screen())
        self.screen_manager.add_widget(self.build_signup_screen())
        self.screen_manager.add_widget(self.build_article_screen())

        return self.screen_manager

    def build_login_screen(self):
        """Builds the login screen layout."""
        login_screen = MDScreen(name='login')
        background = Image(source='shubh 2.jpg', allow_stretch=True, keep_ratio=False)

        layout = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        self.login_username_input = MDTextField(
            hint_text='Enter Username', size_hint=(1, 0.1), mode='round'
        )
        layout.add_widget(self.login_username_input)

        self.login_password_input = MDTextField(
            hint_text='Enter Password', size_hint=(1, 0.1), mode='round', password=True
        )
        layout.add_widget(self.login_password_input)

        login_button = MDRaisedButton(
            text='Login', size_hint=(1, 0), pos_hint={'center_x': 0.5}
        )
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)

        signup_button = MDRaisedButton(
            text='Sign Up', size_hint=(1, 0), pos_hint={'center_x': 0.5}
        )
        signup_button.bind(on_press=self.go_to_signup)
        layout.add_widget(signup_button)

        login_screen.add_widget(background)
        login_screen.add_widget(layout)

        return login_screen

    def build_signup_screen(self):
        """Builds the sign-up screen layout."""
        signup_screen = MDScreen(name='signup')
        background = Image(source='shubh 1.jpg', allow_stretch=True, keep_ratio=False)

        layout = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        self.signup_username_input = MDTextField(
            hint_text='Enter New Username', size_hint=(1, 0.1), mode='round'
        )
        layout.add_widget(self.signup_username_input)

        self.signup_password_input = MDTextField(
            hint_text='Enter New Password', size_hint=(1, 0.1), mode='round', password=True
        )
        layout.add_widget(self.signup_password_input)

        register_button = MDRaisedButton(
            text='Register', size_hint=(1, 0), pos_hint={'center_x': 0.5}
        )
        register_button.bind(on_press=self.register_user)
        layout.add_widget(register_button)

        signup_screen.add_widget(background)
        signup_screen.add_widget(layout)

        return signup_screen

    def build_article_screen(self):
        """Builds the article-fetching screen layout."""
        article_screen = MDScreen(name='article')

        layout = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))

        self.url_input = MDTextField(
            hint_text='Enter Article URL', size_hint=(1, 0.1), mode='round'
        )
        layout.add_widget(self.url_input)

        fetch_button = MDRaisedButton(
            text='Fetch Article', size_hint=(1, 0.1), pos_hint={'center_x': 0.5}
        )
        fetch_button.bind(on_press=self.fetch_article)
        layout.add_widget(fetch_button)

        scroll = ScrollView(size_hint=(1, 0.75))
        self.results_box = MDBoxLayout(
            orientation='vertical', padding=dp(10), spacing=dp(15), size_hint_y=None
        )
        self.results_box.bind(minimum_height=self.results_box.setter('height'))

        self.title_label = MDLabel(
            text='Title: ', size_hint_y=None, height=dp(30), halign='left', font_style='H6'
        )
        self.date_label = MDLabel(
            text='Publication Date: ', size_hint_y=None, height=dp(30), halign='left'
        )
        self.summary_label = MDLabel(
            text='Summary: ', size_hint_y=None, halign='left',
            text_size=(Window.width - dp(40), None), height=dp(400)
        )
        self.sentiment_label = MDLabel(
            text='Sentiment: ', size_hint_y=None, height=dp(30), halign='left'
        )

        self.credibility_label = MDLabel(
            text='Credibility: ', size_hint_y=None, height=dp(30), halign='left'
        )

        self.results_box.add_widget(self.title_label)
        self.results_box.add_widget(self.date_label)
        self.results_box.add_widget(self.summary_label)
        self.results_box.add_widget(self.sentiment_label)
        self.results_box.add_widget(self.credibility_label)
        # Text-to-Speech Button
        tts_button = MDRaisedButton(text='Read Summary', size_hint=(1, 0.1), pos_hint={'center_x': 0.5})
        tts_button.bind(on_press=self.text_to_speech)
        layout.add_widget(tts_button)

        scroll.add_widget(self.results_box)
        layout.add_widget(scroll)
        article_screen.add_widget(layout)

        return article_screen

    def login(self, instance):
        """Handles login by checking the database."""
        username = self.login_username_input.text.strip()
        password = self.login_password_input.text.strip()

        conn = sqlite3.connect('app_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.screen_manager.current = 'article'
        else:
            self.login_username_input.hint_text = 'Invalid credentials! Try again.'

    def register_user(self, instance):
        """Handles user registration."""
        username = self.signup_username_input.text.strip()
        password = self.signup_password_input.text.strip()

        if not username or not password:
            return

        conn = sqlite3.connect('app_data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        self.screen_manager.current = 'login'

    def go_to_signup(self, instance):
        """Switches to the sign-up screen."""
        self.screen_manager.current = 'signup'

    def fetch_article(self, instance):
        """Fetches the article, performs sentiment analysis, and checks credibility."""
        url = self.url_input.text.strip()
        if not url:
            self.update_labels('Invalid URL', '', 'Please enter a valid URL.')
            return

        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            sentiment = self.sentiment_analyzer(article.summary)[0]
            sentiment_label = sentiment['label']
            sentiment_score = sentiment['score']

            credibility = self.check_article_credibility(article.text)  # Use article text for credibility check

            self.update_labels(
                article.title,
                str(article.publish_date),
                article.summary,
                sentiment_label,
                sentiment_score,
                credibility
            )
        except Exception as e:
            self.update_labels('Error fetching article', '', str(e))
    def text_to_speech(self, instance):
        """Reads the title, summary, credibility, and sentiment using Azure's Text-to-Speech."""
        title_text = self.title_label.text.replace('Title: ', '').strip()
        summary_text = self.summary_label.text.replace('Summary: ', '').strip()
        sentiment_text = self.sentiment_label.text.replace('Sentiment: ', '').strip()
        credibility_text = self.credibility_label.text.replace('Credibility: ', '').strip()

        if not summary_text or not title_text:
            print("No title or summary available to read.")
            return  # Exit if there's no text to read

        try:
            # Construct the speech text
            speech_text = (
                f"The summary for the news title {title_text} is: {summary_text}. "
                f"The sentiment is {sentiment_text} and the credibility is {credibility_text}."
            )

            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION
            )
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

            # Select a voice (optional, but recommended)
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

            # Initialize Speech Synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=audio_config
            )

            # Speak the text
            result = synthesizer.speak_text(speech_text)
        
            # Check if the synthesis was successful
            if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"Speech synthesis failed. Reason: {result.reason}")

        except Exception as e:
            print(f"Error in TTS: {e}")




    def update_labels(self, title, date, summary, sentiment_label='', sentiment_score=0, credibility=''):
        """Updates the UI labels with fetched article details."""
        self.title_label.text = f"Title: {title}"
        self.date_label.text = f"Publication Date: {date}"
        self.summary_label.text = f"Summary: {summary}"
        self.sentiment_label.text = f"Sentiment: {sentiment_label} ({sentiment_score:.2f})"
        
        # Set the text color based on credibility
        if credibility == "real":
            self.credibility_label.text = f"Credibility: {credibility}"
            self.credibility_label.color = (0, 1, 0, 1)  # Green color for "real"
        elif credibility == "fake":
            self.credibility_label.text = f"Credibility: {credibility}"
            self.credibility_label.color = (1, 0, 0, 1)  # Red color for "fake"
        else:
            self.credibility_label.text = f"Credibility: {credibility}"
            self.credibility_label.color = (1, 1, 1, 1)  # Default to white for unknown

    def check_article_credibility(self, text):
        """Check if the article is 'fake' or 'real' using a fake news detector."""
        candidate_labels = ["real", "fake"]
        result = self.fake_news_detector(text, candidate_labels)
        credibility = result['labels'][0]  # The top prediction label
        return credibility


if __name__ == "__main__":
    ArticleApp().run()
