import streamlit as st
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

# Set layout and page title
st.set_page_config(page_title="💰 Daily Expense Tracker", layout="wide")

# 👋 Dynamic greeting based on time
current_hour = dt.datetime.now().hour
if current_hour < 12:
    greet = "Good morning ☀️"
elif current_hour < 18:
    greet = "Good afternoon 🌤️"
else:
    greet = "Good evening 🌙"

st.title(f"{greet}, let's track your expenses wisely!")
st.markdown("Keep an eye on your daily spending 💸 and get smart insights into where your money is going 📊.")

# 🔁 Initialize or update session data
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

if "budgets" not in st.session_state:
    st.session_state.budgets = {}

# 📝 Add new expense form
st.subheader("🧾 Add a New Expense")

with st.form("expense_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 When did you spend?", dt.date.today())
    with col2:
        category = st.selectbox("📂 What was it for?", ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"])
    
    amount = st.number_input("💸 How much did you spend? (₹)", min_value=0.0, format="%.2f", step=10.0)
    note = st.text_input("🗒️ Add a note (e.g., Lunch with friends)")

    submitted = st.form_submit_button("➕ Save Expense")

if submitted:
    new_entry = pd.DataFrame([[date, category, amount, note]], columns=st.session_state.expenses.columns)
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_entry], ignore_index=True)
    st.session_state.expenses["Date"] = pd.to_datetime(st.session_state.expenses["Date"])

    st.success(f"✅ Added ₹{amount:.2f} to '{category}' on {date.strftime('%b %d, %Y')}.")

# 📊 Show expenses if data exists
if not st.session_state.expenses.empty:
    df = st.session_state.expenses
    df["Date"] = pd.to_datetime(df["Date"])

    # 📅 Monthly Filter
    st.subheader("📅 Filter by Month")
    month_selected = st.selectbox("Choose a month to view:", sorted(df["Date"].dt.strftime("%B %Y").unique(), reverse=True))
    df_filtered = df[df["Date"].dt.strftime("%B %Y") == month_selected]
    df_filtered["Date"] = pd.to_datetime(df_filtered["Date"])

    if df_filtered.empty:
        st.info("No records for this month. Try selecting a different one.")
    else:
        # 💰 Budget Section
        st.subheader("💰 Set Your Monthly Budget")
        default_budget = st.session_state.budgets.get(month_selected, 1000.0)
        budget_input = st.number_input(f"Set your budget for {month_selected} (₹)", min_value=0.0, value=default_budget, step=100.0, key="budget")

        st.session_state.budgets[month_selected] = budget_input
        total_spent = df_filtered["Amount"].sum()
        remaining_budget = budget_input - total_spent
        budget_used_pct = (total_spent / budget_input * 100) if budget_input > 0 else 0

        st.markdown(f"### 💸 You've spent ₹{total_spent:.2f} of your ₹{budget_input:.2f} budget.")
        st.progress(min(100, int(budget_used_pct)))

        if remaining_budget < 0:
            st.error(f"🚨 Over budget by ₹{-remaining_budget:.2f}!")
        elif budget_used_pct > 90:
            st.warning(f"⚠️ You're over 90% of your budget. Only ₹{remaining_budget:.2f} left.")
        else:
            st.success(f"✅ You're within budget! ₹{remaining_budget:.2f} remaining.")

        # 📋 Expense Table
        st.subheader(f"📋 Expenses in {month_selected}")
        st.dataframe(df_filtered.sort_values("Date", ascending=False), use_container_width=True)

        # 📌 Top 3 categories
        st.markdown("**📌 Top Spending Categories:**")
        top_cats = df_filtered.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        for i, (cat, val) in enumerate(top_cats.items()):
            if i >= 3:
                break
            st.markdown(f"- {cat}: ₹{val:.2f}")

        # ⚠️ Daily overspend alerts
        daily_totals = df_filtered.groupby("Date")["Amount"].sum()
        overspend_days = daily_totals[daily_totals > 500]
        if not overspend_days.empty:
            st.warning("⚠️ You spent more than ₹500 on these days:")
            for date, total in overspend_days.items():
                st.markdown(f"- **{date.strftime('%b %d')}**: ₹{total:.2f}")

        # 📊 Pie Chart: Category breakdown
        st.subheader("📊 Where Your Money Went")
        fig1, ax1 = plt.subplots()
        ax1.pie(top_cats, labels=top_cats.index, autopct="%.1f%%", startangle=140)
        ax1.axis("equal")
        st.pyplot(fig1)

        # 📈 Line Chart: Daily trends
        st.subheader("📈 Daily Spending Trend")
        st.line_chart(daily_totals)

        # 📤 Download CSV
        st.download_button("⬇️ Download This Month's Data", df_filtered.to_csv(index=False), file_name="monthly_expenses.csv")
else:
    st.info("💡 No expenses added yet. Start by entering your first one above!")

# 👣 Friendly footer
st.markdown("---")
st.markdown("Made with ❤️ using [Streamlit](https://streamlit.io) | 💼 Manage your money. Master your month.")
