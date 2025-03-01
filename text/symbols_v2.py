""" from https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
'''
_pad        = '_'
_punctuation = '#;:,.!?¡¿—…"«»“” '
_letters = 'abcdefghijklmnopqrstuvwxyzáàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệỉĩịíìóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ'
_letters_ipa = "ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘'̩'ᵻ-"
_letters_en = 'abcdefghijklmnopqrstuvwxyz'
# Export all symbols:
symbols = [_pad] + list(_punctuation) + list(_letters) + list(_letters_ipa) + list(_letters_en)

# Special symbol ids
SPACE_ID = symbols.index(" ")