import json
import os
import locale
import ctypes
import platform

class Localization:
    def __init__(self):
        self.current_language = 'uk'
        self.translations = {}
        self.supported_languages = ['uk', 'en', 'ru']
        self.load_translations()
        self.detect_language()
    
    def detect_language(self):
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    saved_language = config.get('language')
                    if saved_language and saved_language in self.supported_languages:
                        self.current_language = saved_language
                        return
        except Exception as e:
            print(f"Error loading language from config: {e}")
        
        self.detect_system_language()

    def detect_system_language(self):
        try:
            if platform.system() == 'Windows':
                windll = ctypes.windll.kernel32
                language_id = windll.GetUserDefaultUILanguage()
                
                language_map = {
                    0x0409: 'en',  # English (US)
                    0x0809: 'en',  # English (UK)
                    0x0c09: 'en',  # English (Australia)
                    0x1009: 'en',  # English (Canada)
                    0x1409: 'en',  # English (New Zealand)
                    0x1809: 'en',  # English (Ireland)
                    0x1c09: 'en',  # English (South Africa)
                    0x2009: 'en',  # English (Jamaica)
                    0x2409: 'en',  # English (Caribbean)
                    0x2809: 'en',  # English (Belize)
                    0x2c09: 'en',  # English (Trinidad)
                    
                    0x0422: 'uk',  # Ukrainian
                    
                    0x0419: 'ru',  # Russian
                    0x0819: 'ru',  # Russian (Moldova)
                    0x0c19: 'ru',  # Russian (Belarus)
                }
                
                detected_lang = language_map.get(language_id)
                if detected_lang and detected_lang in self.supported_languages:
                    self.current_language = detected_lang
                    return
            
            try:
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    lang_code = system_locale.split('_')[0].lower()
                    if lang_code in self.supported_languages:
                        self.current_language = lang_code
                        return
            except:
                pass
                
        except Exception as e:
            print(f"Error detecting system language: {e}")
        
        self.current_language = 'uk'
    
    def load_translations(self):
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        
        for lang in self.supported_languages:
            translation_file = os.path.join(translations_dir, f'{lang}.json')
            try:
                if os.path.exists(translation_file):
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    print(f"Translation file not found: {translation_file}")
                    self.translations[lang] = {}
            except Exception as e:
                print(f"Error loading translation file {translation_file}: {e}")
                self.translations[lang] = {}
    
    def get_text(self, key, **kwargs):
        try:
            if self.current_language in self.translations:
                text = self.translations[self.current_language].get(key)
                if text:
                    if kwargs:
                        return text.format(**kwargs)
                    return text
            
            if 'uk' in self.translations:
                text = self.translations['uk'].get(key)
                if text:
                    if kwargs:
                        return text.format(**kwargs)
                    return text
            
            return key
            
        except Exception as e:
            print(f"Error getting translation for key '{key}': {e}")
            return key
    
    def set_language(self, language):
        if language in self.supported_languages:
            old_language = self.current_language
            self.current_language = language
            print(f"Language changed from {old_language} to {language}")
            return True
        return False
    
    def get_current_language(self):
        return self.current_language
    
    def get_supported_languages(self):
        return self.supported_languages.copy()
    
    def get_language_name(self, lang_code):
        language_names = {
            'uk': 'Українська',
            'en': 'English', 
            'ru': 'Русский'
        }
        return language_names.get(lang_code, lang_code)


_localization_instance = None

def get_localization():
    global _localization_instance
    if _localization_instance is None:
        _localization_instance = Localization()
    return _localization_instance

def _(key, **kwargs):
    return get_localization().get_text(key, **kwargs)