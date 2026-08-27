import pandas as pd  # type: ignore[reportMissingModuleSource]
import os
import re


class DataAnalyzer:

    def __init__(self, file_path):

        self.file_path = file_path
        self.df = None

        self.load_data()

    # ==================================================
    # LOAD DATASET
    # ==================================================

    def load_data(self):

        try:

            if not os.path.exists(self.file_path):

                print(
                    f"Dataset not found: {self.file_path}"
                )

                return

            if str(self.file_path).lower().endswith(".csv"):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path)

            # Remove completely empty rows
            self.df = self.df.dropna(
                how="all"
            )

            print(
                "✅ Dataset loaded successfully"
            )

            print(
                "Rows:",
                len(self.df)
            )

            print(
                "Columns:",
                list(self.df.columns)
            )

        except Exception as error:

            print(
                "❌ Dataset loading error:",
                error
            )

    # ==================================================
    # DATA STATUS
    # ==================================================

    def is_loaded(self):

        return self.df is not None and not self.df.empty

    # ==================================================
    # TOTAL ORDERS
    # ==================================================

    def total_orders(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "OrderID" in self.df.columns:

            return (
                f"There are {self.df['OrderID'].nunique():,} "
                f"orders in the dataset."
            )

        return (
            f"There are {len(self.df):,} records "
            f"in the dataset."
        )

    # ==================================================
    # TOTAL REVENUE
    # ==================================================

    def total_revenue(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "TotalPrice" not in self.df.columns:

            return "The TotalPrice column was not found."

        revenue = pd.to_numeric(
            self.df["TotalPrice"],
            errors="coerce"
        ).sum()

        return (
            f"The total revenue is "
            f"${revenue:,.2f}."
        )

    # ==================================================
    # AVERAGE ORDER VALUE
    # ==================================================

    def average_order_value(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "TotalPrice" not in self.df.columns:

            return "The TotalPrice column was not found."

        prices = pd.to_numeric(
            self.df["TotalPrice"],
            errors="coerce"
        )

        average = prices.mean()

        return (
            f"The average order value is "
            f"${average:,.2f}."
        )

    # ==================================================
    # TOTAL QUANTITY
    # ==================================================

    def total_quantity(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "Quantity" not in self.df.columns:

            return "The Quantity column was not found."

        quantity = pd.to_numeric(
            self.df["Quantity"],
            errors="coerce"
        ).sum()

        return (
            f"The total quantity of products "
            f"ordered is {quantity:,.0f}."
        )

    # ==================================================
    # TOP PRODUCT BY QUANTITY
    # ==================================================

    def top_product(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "Product" not in self.df.columns:

            return "The Product column was not found."

        if "Quantity" not in self.df.columns:

            return "The Quantity column was not found."

        temp = self.df.copy()

        temp["Quantity"] = pd.to_numeric(
            temp["Quantity"],
            errors="coerce"
        )

        product_sales = (
            temp.groupby("Product")["Quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        if product_sales.empty:

            return "I couldn't determine the top product."

        product = product_sales.index[0]
        quantity = product_sales.iloc[0]

        return (
            f"The best-selling product is "
            f"{product}, with {quantity:,.0f} "
            f"units sold."
        )

    # ==================================================
    # TOP PRODUCT BY REVENUE
    # ==================================================

    def top_revenue_product(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        required = [
            "Product",
            "TotalPrice"
        ]

        for column in required:

            if column not in self.df.columns:

                return (
                    f"The {column} column "
                    f"was not found."
                )

        temp = self.df.copy()

        temp["TotalPrice"] = pd.to_numeric(
            temp["TotalPrice"],
            errors="coerce"
        )

        revenue = (
            temp.groupby("Product")["TotalPrice"]
            .sum()
            .sort_values(ascending=False)
        )

        if revenue.empty:

            return "I couldn't determine the top product."

        product = revenue.index[0]
        amount = revenue.iloc[0]

        return (
            f"{product} generated the highest "
            f"revenue, with ${amount:,.2f}."
        )

    # ==================================================
    # PAYMENT METHOD
    # ==================================================

    def payment_method(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "PaymentMethod" not in self.df.columns:

            return (
                "The PaymentMethod column "
                "was not found."
            )

        method = (
            self.df["PaymentMethod"]
            .value_counts()
        )

        if method.empty:

            return "No payment method data found."

        name = method.index[0]
        count = method.iloc[0]

        return (
            f"The most popular payment method "
            f"is {name}, used for {count:,} orders."
        )

    # ==================================================
    # ORDER STATUS
    # ==================================================

    def order_status(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "OrderStatus" not in self.df.columns:

            return (
                "The OrderStatus column "
                "was not found."
            )

        status = (
            self.df["OrderStatus"]
            .value_counts()
        )

        result = []

        for name, count in status.items():

            result.append(
                f"{name}: {count:,}"
            )

        return (
            "Order status breakdown: "
            + ", ".join(result)
            + "."
        )

    # ==================================================
    # CANCELLED ORDERS
    # ==================================================

    def cancelled_orders(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "OrderStatus" not in self.df.columns:

            return (
                "The OrderStatus column "
                "was not found."
            )

        cancelled = (
            self.df["OrderStatus"]
            .astype(str)
            .str.lower()
            .str.contains("cancel")
            .sum()
        )

        return (
            f"There are {cancelled:,} "
            f"cancelled orders."
        )

    # ==================================================
    # RETURNED ORDERS
    # ==================================================

    def returned_orders(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "OrderStatus" not in self.df.columns:

            return (
                "The OrderStatus column "
                "was not found."
            )

        returned = (
            self.df["OrderStatus"]
            .astype(str)
            .str.lower()
            .str.contains("return")
            .sum()
        )

        return (
            f"There are {returned:,} "
            f"returned orders."
        )

    # ==================================================
    # REFERRAL SOURCE
    # ==================================================

    def referral_source(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "ReferralSource" not in self.df.columns:

            return (
                "The ReferralSource column "
                "was not found."
            )

        sources = (
            self.df["ReferralSource"]
            .value_counts()
        )

        if sources.empty:

            return "No referral source data found."

        source = sources.index[0]
        count = sources.iloc[0]

        return (
            f"{source} is the most common referral "
            f"source, generating {count:,} orders."
        )

    # ==================================================
    # REFERRAL REVENUE
    # ==================================================

    def referral_revenue(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        required = [
            "ReferralSource",
            "TotalPrice"
        ]

        for column in required:

            if column not in self.df.columns:

                return (
                    f"The {column} column "
                    f"was not found."
                )

        temp = self.df.copy()

        temp["TotalPrice"] = pd.to_numeric(
            temp["TotalPrice"],
            errors="coerce"
        )

        revenue = (
            temp.groupby("ReferralSource")["TotalPrice"]
            .sum()
            .sort_values(ascending=False)
        )

        if revenue.empty:

            return "No referral revenue data found."

        source = revenue.index[0]
        amount = revenue.iloc[0]

        return (
            f"{source} generated the highest referral "
            f"revenue at ${amount:,.2f}."
        )

    # ==================================================
    # COUPON ANALYSIS
    # ==================================================

    def coupon_analysis(self):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "CouponCode" not in self.df.columns:

            return (
                "The CouponCode column "
                "was not found."
            )

        coupons = (
            self.df["CouponCode"]
            .dropna()
            .astype(str)
        )

        coupons = coupons[
            coupons.str.strip() != ""
        ]

        if coupons.empty:

            return "No coupon data found."

        counts = coupons.value_counts()

        coupon = counts.index[0]
        count = counts.iloc[0]

        return (
            f"The most frequently used coupon "
            f"is {coupon}, used {count:,} times."
        )

    # ==================================================
    # DATASET SUMMARY
    # ==================================================

    def summary(self):

        if not self.is_loaded():

            return (
                "The dataset could not be loaded."
            )

        rows = len(self.df)

        columns = len(self.df.columns)

        return (
            f"The dataset contains {rows:,} records "
            f"and {columns} columns."
        )

    # ==================================================
    # SEARCH PRODUCT
    # ==================================================

    def product_info(self, product_name):

        if not self.is_loaded():
            return "Dataset is not loaded."

        if "Product" not in self.df.columns:

            return "The Product column was not found."

        temp = self.df[
            self.df["Product"]
            .astype(str)
            .str.lower()
            .str.contains(
                product_name.lower(),
                na=False
            )
        ]

        if temp.empty:

            return (
                f"I couldn't find any product "
                f"matching {product_name}."
            )

        quantity = 0
        revenue = 0

        if "Quantity" in temp.columns:

            quantity = pd.to_numeric(
                temp["Quantity"],
                errors="coerce"
            ).sum()

        if "TotalPrice" in temp.columns:

            revenue = pd.to_numeric(
                temp["TotalPrice"],
                errors="coerce"
            ).sum()

        return (
            f"{product_name} has sold "
            f"{quantity:,.0f} units and generated "
            f"${revenue:,.2f} in revenue."
        )

    # ==================================================
    # INTELLIGENT QUERY
    # ==================================================

    def answer(self, question):

        q = question.lower().strip()

        # Total orders
        if (
            "how many orders" in q
            or "number of orders" in q
            or "total orders" in q
        ):
            return self.total_orders()

        # Revenue
        if (
            "total revenue" in q
            or "total sales" in q
            or "revenue" in q
        ):
            return self.total_revenue()

        # Average order
        if (
            "average order" in q
            or "average value" in q
            or "average price" in q
        ):
            return self.average_order_value()

        # Quantity
        if (
            "total quantity" in q
            or "units sold" in q
            or "how many products" in q
        ):
            return self.total_quantity()

        # Best-selling product
        if (
            "best selling" in q
            or "best-selling" in q
            or "most sold" in q
            or "top selling" in q
        ):
            return self.top_product()

        # Highest revenue product
        if (
            "highest revenue product" in q
            or "product generated the most revenue" in q
            or "product with the highest revenue" in q
        ):
            return self.top_revenue_product()

        # Payment
        if (
            "payment method" in q
            or "payment" in q
        ):
            return self.payment_method()

        # Status
        if (
            "order status" in q
            or "status breakdown" in q
        ):
            return self.order_status()

        # Cancelled
        if (
            "cancelled" in q
            or "canceled" in q
            or "cancellation" in q
        ):
            return self.cancelled_orders()

        # Returned
        if (
            "returned" in q
            or "return" in q
        ):
            return self.returned_orders()

        # Referral
        if (
            "referral" in q
            or "marketing source" in q
        ):

            if "revenue" in q:

                return self.referral_revenue()

            return self.referral_source()

        # Coupon
        if (
            "coupon" in q
            or "promo code" in q
        ):
            return self.coupon_analysis()

        # Dataset
        if (
            "dataset" in q
            or "data" in q
            or "records" in q
            or "columns" in q
        ):
            return self.summary()

        # Product-specific question
        match = re.search(
            r"(?:about|for|product)\s+([a-zA-Z0-9\s]+)",
            q
        )

        if match:

            product_name = match.group(1).strip()

            if len(product_name) > 2:

                return self.product_info(
                    product_name
                )

        return None