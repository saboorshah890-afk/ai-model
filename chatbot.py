from datetime import datetime
from pathlib import Path

from data_analyzer import DataAnalyzer


class NovaChatbot:

    def __init__(self):

    

        dataset_folder = Path(__file__).resolve().parent
        dataset_files = sorted(
            list(dataset_folder.glob("*.xlsx"))
            + list(dataset_folder.glob("*.csv"))
        )
        dataset_path = (
            dataset_files[0]
            if dataset_files
            else dataset_folder / "Dataset for Data Analytics.xlsx"
        )

        self.analyzer = DataAnalyzer(
            dataset_path
        )

    
    def get_response(self, message):

        if not message:

            return (
                "Please type something so I can "
                "help you."
            )

        question = message.lower().strip()

    

        if question in [
            "exit",
            "quit",
            "bye",
            "goodbye"
        ]:

            return (
                "Goodbye! 👋 Have a great day."
            )

   

        if question in [
            "hi",
            "hello",
            "hey",
            "hey nova",
            "hello nova",
            "hi nova"
        ]:

            return (
                "Hello! 👋 I'm Nova. "
                "I can analyze your e-commerce dataset "
                "and answer questions about sales, "
                "products, orders, payments, coupons, "
                "and referral sources."
            )

        

        if "your name" in question:

            return (
                "My name is Nova. 🤖 "
                "I'm your AI-powered data assistant."
            )

        if "time" in question:

            current_time = datetime.now().strftime(
                "%I:%M %p"
            )

            return (
                f"The current time is "
                f"{current_time}."
            )


        if (
            "today's date" in question
            or "todays date" in question
            or question == "date"
            or "what date" in question
        ):

            current_date = datetime.now().strftime(
                "%B %d, %Y"
            )

            return (
                f"Today's date is "
                f"{current_date}."
            )


        data_response = self.analyzer.answer(
            message
        )

        if data_response:

            return data_response


        if (
            "help" in question
            or "what can you do" in question
        ):

            return (
                "I can analyze your dataset. "
                "Try asking me: "
                "How many orders are there? "
                "What is the total revenue? "
                "Which product sold the most? "
                "What is the average order value? "
                "Which payment method is most popular? "
                "How many orders were cancelled? "
                "Which referral source generated the most revenue?"
            )

        return (
            "I understand your question, but I don't "
            "have a data-analysis rule for it yet. "
            "Try asking about orders, revenue, products, "
            "payments, returns, cancellations, coupons, "
            "or referral sources."
        )
