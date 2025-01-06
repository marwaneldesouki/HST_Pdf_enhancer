from difflib import get_close_matches
import arabic_reshaper
from bidi.algorithm import get_display
correct_lines = ['ﻣﻮﻗﻊ', 'ﺍﻟﻄﺒﺎﻋﺔ:', 'ﻧﻴﺎﺑﺔﺷﺮﻕ', 'ﺍﻟﻘﺎﻫﺮﺓ', 'ﺍﻟﻜﻠﻴﺔ', 'ﻟﺸﺌﻮﻥ', 'ﺍﻻﺳﺮﺓ', 'ﺍﻟﻘﺎﻫﺮﺓ', 'ﺍﻟﺠﺪﻳﺪﺓ', 'ﺍﻟﺠﺰﺋﻴﺔ', 'ﻟﺸﺌﻮﻥ', 'ﺍﻻﺳﺮﺓ', 'ﻧﻴﺎﺑﺔ', 'ﺃﺟﻨﺪﺓ', 'ﻳﻮﻣﻴﺔ', 'ﺟﻠﺴﺎﺕ', 'ﻧﻤﻮﺫﺝ', 'ﺭﻗﻢ', '42', 'ﺷﺌﻮﻥ', 'ﺃﺳﺮﺓ', '19', 'ﺑﺪﺍﺋﺮﺓ', '2024/12/16', 'ﻳﻮﻣﻴﺔ', 'ﺟﻠﺴﺔ', 'ﻳﻮﻡ', 'ﺍﻟﻤﻮﺍﻓﻖ', 'ﺭﺋﻴﺲ', 'ﺍﻟﻤﺤﻜﻤﺔ', 'ﻧﺰﺍﺭ', 'ﻋﺒﺪﺍﻟﻔﺘﺎﺡ', 'ﺑﺮﺋﺎﺳﺔ', 'ﺍﻟﻘﺎﺿﻲ', 'ﺍﻟﻘﺎﺿﻴﻴﻦ', 'ﻣﺤﻤﺪ', 'ﺍﻟﺸﻌﺮﺍﻭﻯ', 'ﻭ', 'ﻣﺤﻤﻮﺩ', 'ﺩﻳﺎﺏ', 'ﻭﻋﻀﻮﻳﺔ', 'ﻛﻞ', 'ﻣﻦ', 'ﻛﺮﻳﻢ', 'ﺣﺴﻦ', 'ﻋﻀﻮ', 'ﺍﻟﺪﺍﺋﺮﺓ', 'ﺍﻟﺨﺎﻣﺲ', 'ﺿﻴﺎﺀ', 'ﺍﻟﺪﻳﻦ', 'ﺍﻻﺣﻤﺪﺍﻭﻯ', 'ﻭﺑﺤﻀﻮﺭ', 'ﻭﺑﺤﻀﻮﺭ', 'ﻋﻀﻮ', 'ﺍﻟﺪﺍﺋﺮﺓ', 'ﺍﻟﺮﺍﺑﻊ', 'ﺍﺣﻤﺪ', 'ﻣﺪﺣﺖ', 'ﻧﻮﺭ', 'ﺍﻟﺪﻳﻦ', 'ﺍﺣﻤﺪ', 'ﻋﻀﻮ', 'ﺍﻟﻨﻴﺎﺑﺔ', 'ﻭﺑﺤﻀﻮﺭ', 'ﻭﺑﺤﻀﻮﺭ', 'ﺍﻟﺨﺒﻴﺮﻳﻦ', 'ﻣﻨﻰ', 'ﻓﺎﻳﺰ', 'ﺍﺑﻮﺍﻟﻮﻓﺎ', 'ﻣﺤﻤﺪ', 'ﺍﻣﻴﺮﻩ', 'ﻋﺎﻃﻒ', 'ﻋﺒﺪﺍﻟﺮﺍﺯﻕ', 'ﺧﺒﻴﺮ', 'ﻧﻔﺴﻲ', 'ﺧﺒﻴﺮ', 'ﺍﺟﺘﻤﺎﻋﻲ', 'ﻧﺎﺻﺮ', 'ﺳﺎﻣﻰ', 'ﻋﻄﻴﻪ', 'ﺧﻠﻴﻞ', 'ﺳﻜﺮﺗﻴﺮ', 'ﺍﻟﺠﻠﺴﺔ', 'ﻭﺑﺤﻀﻮﺭ', 'ﻓﺘﺤﺖ', 'ﺍﻟﺠﻠﺴﺔ', 'ﺍﻟﺴﺎﻋﻪ', 'ﻭﻗﻔﻠﺖ', 'ﺍﻟﺴﺎﻋﺔ']
def fix_arabic_text(cell): # Fix Arabic text direction
    try:
        reshaped_text = arabic_reshaper.reshape(cell)  # Reshape Arabic characters
        bidi_text = get_display(reshaped_text)  # Apply BiDi algorithm
        return bidi_text
    except Exception:
        return cell  # Return as is if not Arabic
correct_lines = [fix_arabic_text(line) for line in correct_lines]
print(correct_lines)
print(get_close_matches(fix_arabic_text('الساغة'), correct_lines, n=1, cutoff=0.7))