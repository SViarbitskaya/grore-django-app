from modeltranslation.translator import translator, TranslationOptions
from images.models import Image

class ImageTranslationOptions(TranslationOptions):
    fields = ('note',)

translator.register(Image, ImageTranslationOptions)
