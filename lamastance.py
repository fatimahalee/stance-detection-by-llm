import requests
import pandas as pd
from time import sleep

# Define the DeepSeek API URL
url = "http://192.168.5.231:24567/v1/chat/completions"
headers = {"Content-Type": "application/json"}


def deepseek_match_claim(news_text, taj_text, row_num):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": """شما یک کارشناس در زمینه تأیید ادعاها بر اساس اخبار هستید. با در نظر گرفتن یک خبر و یک پست، تعیین کنید که آیا خبر ادعاهای مطرح شده در پست را تأیید می‌کند یا خیر. با "بله"، "خیر" یا "نامربوط" پاسخ دهید. 
             "بله" اگر خبر ادعاهای مطرح شده در پست را تأیید کند و هردو محتوا راجع به یک موضوع دقیقا یکسان صحبت کنند.

              "خیر" اگر خبر به وضوح و به طور کامل ادعای مطرح شده در پست را رد کند و اطلاعاتی ارائه دهد که مستقیماً
              آن ادعا را نفی کند و کاملا با آن در تضاد باشد. تأکید می شود که پاسخ "خیر" فقط زمانی داده می شود که
              خبر به طور مستقیم و کامل با ادعای پست تناقض داشته باشد.
              "نامربوط" اگر خبر به ادعای مطرح شده در پست نپردازد یا اطلاعات اضافی ارائه دهد یا ارتباط کمی با آن داشته باشد.
              مثلا اگر یک محتوا بگوید رویدادی از 1 مهر شروع می شود در حالی که دیگری بگوید دقیقا همان رویداد از تاریخ دیگری شروع می شود، تناقض وجود دارد.
             مثلا اگر یک محتوا علت چیزی را بیان کرده و دیگری به آن اشاره نکرده، اطلاعات اضافی است و تناقضی وجود ندارد و پاسخ خیر نیست. 
             مثلا اگر یکی از محتواها به یک مقام مسئول اشاره کرده و دیگری نام آن شخص را ذکر کرده باشد، تناقضی وجود ندارد و پاسخ خیر نیست. 
              مثلا اگر یک محتوا راجع به شهر تهران چیزی را گفته باشد و دیگری راجع به شهر دیگری هم مشابه آن را گفته باشد، تناقضی وجود ندارد و پاسخ خیر نیست.
              مثلا اگر یک محتوا بگوید رییس جمهور به عراق رفت و دیگری بگوید رییس جمهور با همتای عراقی خود دیدار کرد، تناقضی وجود ندارد. یا اگر بگوید رییس جمهور به بغداد رفت، تناقضی وجود ندارد چون بغداد پایتخت عراق است. یا اگر بگوید در عراق هدیه ای از همتای خود دریافت کرد، تناقضی وجود ندارد و پاسخ خیر نیست.
              اگر هم چیزی را نمی دانستی، پاسخ "نامربوط" را انتخاب کن.
              اگر پاسخ شما "خیر" یا "نامربوط" بود، علت پاسخ را هم در خط بعدی بیان کن. """
            },
            {"role": "user", "content": f"خبر: {news_text}\n ادعا: {taj_text}"}
        ]
    }

    while True:
        try:
            print(f"Processing row {row_num}...")
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"Error: Received status code {response.status_code}, Retrying in 5 seconds...")
                sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}. Retrying in 5 seconds...")
            sleep(5)


# Load the dataset
file_path = "claim8000_final.xlsx"
df = pd.read_excel(file_path)

# Define a threshold for request length
MAX_REQUEST_LENGTH = 7000  # مقدار تقریبی برای جلوگیری از خطای 400


def process_claims():
    results = []
    for row_number in range(len(df)):
        try:
            claim = str(df.at[row_number, "پست"])
            news = str(df.at[row_number, "خبر"])

            # Construct the full message text
            full_message = f"خبر: {news}\n ادعا: {claim}"

            # Check if the request is too long
            if len(full_message) > MAX_REQUEST_LENGTH:
                print(f"Skipping row {row_number} due to excessive length ({len(full_message)} characters).")
                results.append("Skipped due to length")
                continue

            # Call the function to get the claim matching result
            result = deepseek_match_claim(news, claim, row_number)
            results.append(result)
            print(f"Row {row_number}: {result}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred at row {row_number}: {e}")
            results.append("Error")
        except Exception as e:
            print(f"Unexpected error at row {row_number}: {e}")
            results.append("Error")

    return results


# Process all claims and store the results
df["lama"] = process_claims()

# Save results to a new Excel file
df.to_excel("claim8000_final_lama.xlsx", index=False)
print("Claim Matching Completed and Saved to 8000")

# Load the dataset
file_path1 = "test_stance_data2.xlsx"
df1 = pd.read_excel(file_path1)

# Process all claims and store the results
df1["lama"] = process_claims()

# Save results to a new Excel file
df1.to_excel("test2stance_deepseek.xlsx", index=False)
print("Claim Matching Completed and Saved to teststance")


