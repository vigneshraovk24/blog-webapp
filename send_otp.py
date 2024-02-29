import smtplib

MY_MAIL = "ramkumartestprograms@gmail.com"
MY_PASSWORD = "uibahjdtxvqxspbk"


class Sendmail:
    def mail(self, to_mail, name, verification_code):
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=MY_MAIL, password=MY_PASSWORD)
            connection.sendmail(from_addr=MY_MAIL, to_addrs=to_mail,
                                msg=f"Subject:blog verification code\n\n {name} your verification code: {verification_code}")

