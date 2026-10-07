import ollama
import streamlit as st
import pandas as pd
import json
from datetime import datetime


# -----------------------------
# PAGE SETTINGS
# -----------------------------

st.set_page_config(
    page_title="AI Expense Categoriser",
    page_icon="💰"
)


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.title("⚙️ Expense Settings")

    categories = [
        "Food",
        "Transport",
        "Shopping",
        "Entertainment",
        "Bills",
        "Healthcare",
        "Education",
        "Travel",
        "Rent",
        "Other"
    ]

    st.write("📂 Expense Categories")

    for category in categories:
        st.write("•", category)

    st.divider()

    if st.button("🗑️ Clear Expenses"):

        st.session_state.expenses = []

        st.success("Expense history cleared! ✅")


# -----------------------------
# SESSION STATE
# -----------------------------

if "expenses" not in st.session_state:
    st.session_state.expenses = []


# -----------------------------
# TITLE
# -----------------------------

st.title(":orange[💰 AI Expense Categoriser]")


st.write(
    "Tell me about your expense and I will automatically "
    "find the amount and category 🤖"
)


# -----------------------------
# SHOW OLD EXPENSES
# -----------------------------

for expense in st.session_state.expenses:

    with st.chat_message("user"):

        st.write(expense["input"])

    with st.chat_message("assistant"):

        st.write(
            f"💰 **Amount:** ₹{expense['amount']}\n\n"
            f"📝 **Description:** {expense['description']}\n\n"
            f"📂 **Category:** {expense['category']}"
        )


# -----------------------------
# CHAT INPUT
# -----------------------------

question = st.chat_input(
    "Example: I spent ₹500 on pizza"
)


# -----------------------------
# PROCESS EXPENSE
# -----------------------------

if question:

    # Show user input

    with st.chat_message("user"):

        st.write(question)


    # AI prompt

    prompt = f"""
You are an AI expense categorisation assistant.

Understand the user's expense.

Find:

1. Amount
2. Description
3. Category

Choose ONLY one category from:

Food
Transport
Shopping
Entertainment
Bills
Healthcare
Education
Travel
Rent
Other

Return ONLY JSON.

Example:

{{
    "amount": 500,
    "description": "Pizza",
    "category": "Food"
}}

User expense:

{question}
"""


    # Ask Ollama

    with st.spinner("AI is understanding your expense... 💭"):

        try:

            response = ollama.chat(

                model="llama3.2:3b",

                messages=[

                    {
                        "role": "system",
                        "content": prompt
                    },

                    {
                        "role": "user",
                        "content": question
                    }

                ]

            )


            answer = response["message"]["content"]

            # Remove markdown if AI adds it

            answer = answer.replace(
                "```json", ""
            )

            answer = answer.replace(
                "```", ""
            )

            answer = answer.strip()


            # Convert AI response to JSON

            result = json.loads(answer)


            amount = float(
                result.get("amount", 0)
            )

            description = result.get(
                "description",
                question
            )

            category = result.get(
                "category",
                "Other"
            )


            # Make sure category is valid

            if category not in categories:

                category = "Other"


            # Save expense

            expense = {

                "input": question,

                "amount": amount,

                "description": description,

                "category": category,

                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )

            }


            st.session_state.expenses.append(
                expense
            )


            # Show result

            with st.chat_message("assistant"):

                st.write(
                    f"💰 **Amount:** ₹{amount:,.2f}"
                )

                st.write(
                    f"📝 **Description:** {description}"
                )

                st.write(
                    f"📂 **Category:** {category}"
                )

                st.success(
                    "Expense added successfully! ✅"
                )


        except Exception as e:

            st.error(
                "Something went wrong while connecting to Ollama."
            )

            st.write(
                "Please make sure Ollama is running "
                "and llama3.2:3b is installed."
            )

            st.code(str(e))


# -----------------------------
# EXPENSE DASHBOARD
# -----------------------------

if st.session_state.expenses:

    st.divider()

    st.subheader("📊 Expense Dashboard")


    # Convert to dataframe

    df = pd.DataFrame(
        st.session_state.expenses
    )


    # Total expense

    total = df["amount"].sum()


    # Number of expenses

    count = len(df)


    # Average expense

    average = df["amount"].mean()


    # Dashboard cards

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "💰 Total Spent",
            f"₹{total:,.2f}"
        )


    with col2:

        st.metric(
            "🧾 Expenses",
            count
        )


    with col3:

        st.metric(
            "📌 Average",
            f"₹{average:,.2f}"
        )


    # -----------------------------
    # CATEGORY SUMMARY
    # -----------------------------

    st.subheader("📂 Category-wise Spending")


    category_total = (

        df.groupby("category")["amount"]

        .sum()

        .reset_index()

    )


    st.bar_chart(

        category_total.set_index(
            "category"
        )

    )


    # -----------------------------
    # EXPENSE TABLE
    # -----------------------------

    st.subheader("🧾 Expense History")


    st.dataframe(

        df[
            [
                "date",
                "description",
                "amount",
                "category"
            ]
        ],

        use_container_width=True,

        hide_index=True

    )