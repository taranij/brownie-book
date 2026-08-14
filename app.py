import streamlit as st
from datetime import date
from html import escape
from supabase import create_client

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Brownie Book",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SUPABASE
# =========================================================

sb = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================================================
# PRODUCTS
# price, profit
# =========================================================

PRODUCTS = {
    "250g Classic": (170, 91),
    "250g Milk Chocolate": (185, 106),
    "250g White Chocolate": (180, 100),
    "250g Triple Chocolate": (200, 120),
    "250g Double Chocolate": (190, 110),
    "250g Oreo": (175, 90),

    "500g Classic": (270, 126),
    "500g Milk Chocolate": (290, 146),
    "500g White Chocolate": (285, 140),
    "500g Triple Chocolate": (310, 164),
    "500g Double Chocolate": (300, 154),
    "500g Oreo": (280, 160),

    "Cookie Pie Dark": (175, 85),
    "Cookie Pie White": (180, 88),
    "Cookie Pie Milk": (185, 94),

    "Brownie Bites": (169, 86),
}

# =========================================================
# COMBOS
#
# selling price, making cost
# 299 Combo:
# customer pays ₹259
# making cost = ₹100
# profit = ₹159
#
# The original "299" is the advertised combo value.
# Actual sale price here is ₹259.
# =========================================================

COMBOS = {
    "299 Combo": (259, 100)
}

# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "order_items" not in st.session_state:
    st.session_state.order_items = []

if "order_customer" not in st.session_state:
    st.session_state.order_customer = ""


# =========================================================
# HELPERS
# =========================================================

def go(page):
    st.session_state.page = page
    st.rerun()


def money(value):
    return f"₹{float(value):,.0f}"


def filt(rows, start=None, end=None):
    return [
        r for r in rows
        if (not start or str(r["date"])[:10] >= start)
        and (not end or str(r["date"])[:10] <= end)
    ]


def load_data():

    sales_response = (
        sb.table("sales")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    purchases_response = (
        sb.table("purchases")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return (
        sales_response.data or [],
        purchases_response.data or []
    )


def add_order_item(name, price, cost, qty):

    st.session_state.order_items.append({
        "product": name,
        "quantity": int(qty),
        "price": float(price),
        "cost": float(cost)
    })


# =========================================================
# UI STYLE
# =========================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap'
);

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

#MainMenu,
footer,
header {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(
            circle at 5% 0%,
            rgba(121, 74, 48, .08),
            transparent 28%
        ),
        radial-gradient(
            circle at 95% 10%,
            rgba(202, 155, 115, .10),
            transparent 25%
        ),
        #fbf8f5;
}

.block-container {
    max-width: 1180px;
    padding: 1.2rem 1.3rem 4rem;
}

/* =====================================================
   BRAND
===================================================== */

.brand {
    background:
        linear-gradient(
            135deg,
            #24130d 0%,
            #4a2417 55%,
            #6d3824 100%
        );

    padding: 1.7rem 1.8rem;
    border-radius: 28px;
    color: white;
    margin-bottom: 1rem;

    box-shadow:
        0 12px 35px rgba(54, 29, 19, .15);

    position: relative;
    overflow: hidden;
}

.brand:after {
    content: "🍫";
    position: absolute;
    right: 28px;
    top: 18px;
    font-size: 4rem;
    opacity: .13;
    transform: rotate(12deg);
}

.brand-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -.5px;
}

.brand-sub {
    margin-top: 4px;
    opacity: .76;
    font-size: .92rem;
}

/* =====================================================
   BUTTONS
===================================================== */

div.stButton > button {
    border-radius: 14px;
    min-height: 44px;
    font-weight: 600;
    border: 1px solid #e7ddd7;
    background: rgba(255,255,255,.95);
    transition: all .15s ease;
}

div.stButton > button:hover {
    border-color: #8b5b43;
    transform: translateY(-1px);
}

/* =====================================================
   TITLES
===================================================== */

.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #2d1b14;
    margin: 1.2rem 0 .7rem;
}

.section-sub {
    color: #806f66;
    font-size: .9rem;
    margin-top: -.35rem;
    margin-bottom: .8rem;
}

/* =====================================================
   METRIC CARDS
===================================================== */

.metric-card {
    background: rgba(255,255,255,.96);
    border: 1px solid #eadfd8;
    border-radius: 21px;
    padding: 1.1rem 1.15rem;
    min-height: 118px;

    box-shadow:
        0 7px 24px rgba(64, 37, 25, .055);
}

.metric-icon {
    font-size: 1.25rem;
}

.metric-label {
    color: #806f66;
    font-size: .78rem;
    font-weight: 600;
    margin-top: .45rem;
}

.metric-value {
    color: #2c1a13;
    font-size: 1.65rem;
    font-weight: 700;
    margin-top: .12rem;
}

.metric-note {
    color: #a18e84;
    font-size: .72rem;
    margin-top: .15rem;
}

/* =====================================================
   ORDER CARD
===================================================== */

.order-card {
    background: white;
    border: 1px solid #eadfd8;
    border-radius: 19px;
    padding: 1rem 1.1rem;
    margin-bottom: .7rem;

    box-shadow:
        0 5px 18px rgba(54, 29, 19, .04);
}

.order-name {
    font-weight: 700;
    color: #332017;
}

.order-details {
    color: #76655d;
    font-size: .82rem;
    margin-top: .25rem;
    line-height: 1.5;
}

.order-price {
    font-size: 1.1rem;
    font-weight: 700;
    color: #5b2c1c;
}

.order-profit {
    font-size: .78rem;
    color: #55735c;
}

/* =====================================================
   ACTION CARD
===================================================== */

.action-card {
    background: white;
    border: 1px solid #eadfd8;
    border-radius: 20px;
    padding: 1rem 1.1rem;
    margin-bottom: .7rem;
}

.action-title {
    font-weight: 700;
    color: #352119;
    font-size: 1rem;
}

.action-desc {
    color: #8a7770;
    font-size: .78rem;
    margin-top: .2rem;
}

/* =====================================================
   SUMMARY
===================================================== */

.summary-box {
    background:
        linear-gradient(
            135deg,
            #fffaf6,
            #f8eee8
        );

    border: 1px solid #ead9cf;
    border-radius: 22px;
    padding: 1.2rem;
    margin-top: .8rem;
}

.summary-row {
    display: flex;
    justify-content: space-between;
    padding: .35rem 0;
    color: #69564d;
}

.summary-total {
    display: flex;
    justify-content: space-between;
    padding-top: .75rem;
    margin-top: .45rem;
    border-top: 1px solid #e4d4ca;
    font-weight: 700;
    color: #2e1a12;
    font-size: 1.05rem;
}

/* =====================================================
   PROFIT
===================================================== */

.profit-box {
    background:
        linear-gradient(
            135deg,
            #edf7ef,
            #f7fbf6
        );

    border: 1px solid #d6e8d8;
    border-radius: 20px;
    padding: 1rem 1.1rem;
    margin-top: .7rem;
}

.profit-label {
    color: #6c806f;
    font-size: .78rem;
}

.profit-value {
    color: #345b3b;
    font-size: 1.7rem;
    font-weight: 700;
    margin-top: .15rem;
}

/* =====================================================
   EMPTY STATE
===================================================== */

.empty {
    text-align: center;
    padding: 2.2rem 1rem;
    background: white;
    border: 1px dashed #decfc7;
    border-radius: 22px;
    color: #89766e;
}

.empty-icon {
    font-size: 2.4rem;
    margin-bottom: .4rem;
}

/* =====================================================
   PILL
===================================================== */

.pill {
    display: inline-block;
    padding: .3rem .65rem;
    border-radius: 999px;
    background: #f2e7df;
    color: #6c3926;
    font-size: .72rem;
    font-weight: 600;
}

/* =====================================================
   INPUTS
===================================================== */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
textarea {
    border-radius: 13px !important;
}

/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 700px) {

    .block-container {
        padding: .7rem .65rem 3rem;
    }

    .brand {
        padding: 1.25rem 1.15rem;
        border-radius: 22px;
    }

    .brand-title {
        font-size: 1.65rem;
    }

    .brand-sub {
        font-size: .78rem;
        max-width: 75%;
    }

    .metric-card {
        min-height: 100px;
        padding: .85rem;
    }

    .metric-value {
        font-size: 1.35rem;
    }

    .section-title {
        font-size: 1.15rem;
    }

    div.stButton > button {
        min-height: 48px;
    }
}

</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div class="brand">

    <div class="brand-title">
        Brownie Book 🍫
    </div>

    <div class="brand-sub">
        Your little business, beautifully organised.
    </div>

</div>
""",
    unsafe_allow_html=True
)

# =========================================================
# NAVIGATION
# =========================================================

nav = st.columns(4)

nav_items = [
    ("🏠", "Dashboard"),
    ("➕", "Add Sale"),
    ("🛒", "Purchase"),
    ("📊", "Reports")
]

for col, (icon, page_name) in zip(
    nav,
    nav_items
):

    with col:

        if st.button(
            f"{icon} {page_name}",
            use_container_width=True
        ):
            go(page_name)


# =========================================================
# LOAD DATA
# =========================================================

today = date.today().isoformat()
month = date.today().replace(day=1).isoformat()

sales, purchases = load_data()

page = st.session_state.page


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    month_sales = filt(
        sales,
        month,
        today
    )

    month_purchases = filt(
        purchases,
        month,
        today
    )

    total_sales = sum(
        float(x["sales"])
        for x in month_sales
    )

    total_profit = sum(
        float(x["profit"])
        for x in month_sales
    )

    ingredient_spend = sum(
        float(x["amount"])
        for x in month_purchases
    )

    total_items = sum(
        int(x["quantity"])
        for x in month_sales
    )

    st.markdown(
        '<div class="section-title">'
        'Good to see you 👋'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Here is how your brownie business is doing this month.'
        '</div>',
        unsafe_allow_html=True
    )

    # METRICS

    metric_cols = st.columns(4)

    metrics = [
        ("💰", "Sales", total_sales, "Money received"),
        ("📈", "Profit", total_profit, "Product profit"),
        ("🛒", "Ingredients", ingredient_spend, "Money spent"),
        ("📦", "Items sold", total_items, "Units sold")
    ]

    for col, (
        icon,
        label,
        value,
        note
    ) in zip(
        metric_cols,
        metrics
    ):

        with col:

            display = (
                money(value)
                if label != "Items sold"
                else f"{int(value):,}"
            )

            st.markdown(
                f"""
<div class="metric-card">

    <div class="metric-icon">
        {icon}
    </div>

    <div class="metric-label">
        {label}
    </div>

    <div class="metric-value">
        {display}
    </div>

    <div class="metric-note">
        {note}
    </div>

</div>
""",
                unsafe_allow_html=True
            )

    # QUICK ACTIONS

    st.markdown(
        '<div class="section-title">'
        'Quick actions'
        '</div>',
        unsafe_allow_html=True
    )

    a, b = st.columns(2)

    with a:

        if st.button(
            "➕  Create new order",
            use_container_width=True
        ):
            go("Add Sale")

    with b:

        if st.button(
            "🛒  Record ingredient purchase",
            use_container_width=True
        ):
            go("Purchase")

    # RECENT ORDERS

    st.markdown(
        '<div class="section-title">'
        'Recent orders'
        '</div>',
        unsafe_allow_html=True
    )

    if not sales:

        st.markdown(
            """
<div class="empty">

    <div class="empty-icon">
        🍫
    </div>

    <strong>
        No orders yet
    </strong>

    <br>

    Your future brownie orders will appear here.

</div>
""",
            unsafe_allow_html=True
        )

    else:

        for r in sales[:7]:

            customer = (
                r.get("customer_name", "")
                or ""
            ).strip()

            details = (
                r.get("order_details", "")
                or ""
            ).strip()

            title = (
                escape(customer)
                if customer
                else "Walk-in / No name"
            )

            detail_text = (
                escape(details)
                if details
                else escape(
                    str(
                        r.get(
                            "product",
                            ""
                        )
                    )
                )
            )

            st.markdown(
                f"""
<div class="order-card">

    <div class="order-name">
        👤 {title}
    </div>

    <div class="order-details">
        {detail_text}
    </div>

    <div class="order-details">
        📅 {escape(str(r["date"])[:10])}
    </div>

    <div style="margin-top:10px;">

        <span class="order-price">
            {money(r["sales"])}
        </span>

        &nbsp;&nbsp;

        <span class="order-profit">
            +{money(r["profit"])} profit
        </span>

    </div>

</div>
""",
                unsafe_allow_html=True
            )


# =========================================================
# ADD SALE
# =========================================================

elif page == "Add Sale":

    st.markdown(
        '<div class="section-title">'
        'Create an order ✨'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Add everything the customer ordered, then enter what they actually paid.'
        '</div>',
        unsafe_allow_html=True
    )

    # CUSTOMER

    customer_name = st.text_input(
        "Customer name",
        value=st.session_state.order_customer,
        placeholder="Optional — just for your reference"
    )

    st.session_state.order_customer = customer_name

    # ADD ITEMS

    st.markdown(
        '<div class="section-title">'
        'Add items'
        '</div>',
        unsafe_allow_html=True
    )

    item_type = st.radio(
        "Choose what you are adding",
        [
            "🍫 Product",
            "🎁 Combo"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    if item_type == "🍫 Product":

        selected = st.selectbox(
            "Product",
            list(PRODUCTS.keys())
        )

        price, normal_profit = PRODUCTS[selected]

        cost = price - normal_profit

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

        st.markdown(
            f"""
<div class="action-card">

    <div class="action-title">
        {escape(selected)}
    </div>

    <div class="action-desc">
        {money(price)} each
        &nbsp; • &nbsp;
        {money(normal_profit)} profit each
    </div>

</div>
""",
            unsafe_allow_html=True
        )

    else:

        selected = st.selectbox(
            "Combo",
            list(COMBOS.keys())
        )

        price, cost = COMBOS[selected]

        normal_profit = price - cost

        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=100,
            value=1,
            step=1
        )

        st.markdown(
            f"""
<div class="action-card">

    <div class="action-title">
        🎁 {escape(selected)}
    </div>

    <div class="action-desc">
        Customer price {money(price)}
        &nbsp; • &nbsp;
        Making cost {money(cost)}
        &nbsp; • &nbsp;
        Profit {money(normal_profit)}
    </div>

</div>
""",
            unsafe_allow_html=True
        )

    if st.button(
        "＋ Add to order",
        use_container_width=True
    ):

        add_order_item(
            selected,
            price,
            cost,
            qty
        )

        st.success(
            f"{selected} × {qty} added."
        )

    # CURRENT ORDER

    if st.session_state.order_items:

        st.markdown(
            '<div class="section-title">'
            'Your order 🧾'
            '</div>',
            unsafe_allow_html=True
        )

        normal_total = 0
        total_cost = 0
        total_quantity = 0

        for i, item in enumerate(
            st.session_state.order_items
        ):

            line_total = (
                item["price"]
                * item["quantity"]
            )

            line_cost = (
                item["cost"]
                * item["quantity"]
            )

            normal_total += line_total
            total_cost += line_cost

            total_quantity += item["quantity"]

            c1, c2, c3 = st.columns(
                [5, 2, 1]
            )

            with c1:

                st.markdown(
                    f"""
<div class="order-card">

    <div class="order-name">
        {escape(item["product"])}
    </div>

    <div class="order-details">
        Quantity: {item["quantity"]}
    </div>

</div>
""",
                    unsafe_allow_html=True
                )

            with c2:

                st.markdown(
                    f"""
<div style="
    padding-top:15px;
    text-align:right;
    font-weight:700;
">

    {money(line_total)}

</div>
""",
                    unsafe_allow_html=True
                )

            with c3:

                if st.button(
                    "✕",
                    key=f"remove_{i}"
                ):

                    st.session_state.order_items.pop(i)

                    st.rerun()

        # SUMMARY

        st.markdown(
            f"""
<div class="summary-box">

    <div class="summary-row">

        <span>
            Normal total
        </span>

        <strong>
            {money(normal_total)}
        </strong>

    </div>

    <div class="summary-row">

        <span>
            Total making cost
        </span>

        <strong>
            {money(total_cost)}
        </strong>

    </div>

</div>
""",
            unsafe_allow_html=True
        )

        # PAYMENT

        st.markdown(
            '<div class="section-title">'
            'Payment'
            '</div>',
            unsafe_allow_html=True
        )

        amount_paid = st.number_input(
            "Amount actually paid by customer",
            min_value=0.0,
            value=float(normal_total),
            step=1.0
        )

        discount = normal_total - amount_paid

        actual_profit = (
            amount_paid
            - total_cost
        )

        if discount > 0:

            st.markdown(
                f"""
<div class="action-card">

    <div class="action-title">
        🏷️ Discount given
    </div>

    <div class="action-desc">

        You reduced the order by

        <strong>
            {money(discount)}
        </strong>

    </div>

</div>
""",
                unsafe_allow_html=True
            )

        elif discount == 0:

            st.markdown(
                '<span class="pill">'
                'No discount'
                '</span>',
                unsafe_allow_html=True
            )

        else:

            st.info(
                f"Customer paid "
                f"{money(abs(discount))} "
                "more than the normal total."
            )

        # PROFIT

        st.markdown(
            f"""
<div class="profit-box">

    <div class="profit-label">
        YOUR PROFIT FROM THIS ORDER
    </div>

    <div class="profit-value">
        {money(actual_profit)}
    </div>

</div>
""",
            unsafe_allow_html=True
        )

        # SAVE

        if st.button(
            "💾  Save order",
            use_container_width=True
        ):

            if amount_paid <= 0:

                st.error(
                    "Amount paid must be greater than ₹0."
                )

            else:

                details = " | ".join(
                    [
                        f"{x['product']} × {x['quantity']}"
                        for x in st.session_state.order_items
                    ]
                )

                sb.table("sales").insert({
                    "date": today,
                    "product": "Order",
                    "quantity": total_quantity,
                    "sales": amount_paid,
                    "profit": actual_profit,
                    "customer_name": customer_name.strip(),
                    "order_details": details
                }).execute()

                st.session_state.order_items = []

                st.session_state.order_customer = ""

                st.success(
                    "Order saved successfully 🎉"
                )

                st.rerun()

        # CLEAR

        if st.button(
            "Clear order",
            use_container_width=True
        ):

            st.session_state.order_items = []

            st.session_state.order_customer = ""

            st.rerun()

    else:

        st.markdown(
            """
<div class="empty">

    <div class="empty-icon">
        🧾
    </div>

    <strong>
        Your order is empty
    </strong>

    <br>

    Add brownies or a combo above.

</div>
""",
            unsafe_allow_html=True
        )


# =========================================================
# PURCHASE
# =========================================================

elif page == "Purchase":

    st.markdown(
        '<div class="section-title">'
        'Ingredient spending 🛒'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'Record the money you actually spend buying ingredients.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.form("purchase"):

        item = st.text_input(
            "What did you buy?",
            placeholder="Chocolate, butter, cocoa powder..."
        )

        amount = st.number_input(
            "Amount spent",
            min_value=0.0,
            step=10.0
        )

        submitted = st.form_submit_button(
            "💾 Save purchase",
            use_container_width=True
        )

        if submitted:

            if not item.strip() or amount <= 0:

                st.error(
                    "Please enter the item and amount."
                )

            else:

                sb.table("purchases").insert({
                    "date": today,
                    "item": item.strip(),
                    "amount": amount
                }).execute()

                st.success(
                    "Purchase saved 🛒"
                )

                st.rerun()


# =========================================================
# REPORTS
# =========================================================

elif page == "Reports":

    st.markdown(
        '<div class="section-title">'
        'Your reports 📊'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-sub">'
        'See your sales, profits and ingredient spending.'
        '</div>',
        unsafe_allow_html=True
    )

    mode = st.radio(
        "Period",
        [
            "This month",
            "All time",
            "Custom"
        ],
        horizontal=True
    )

    start = None
    end = None

    if mode == "This month":

        start = month
        end = today

    elif mode == "Custom":

        a, b = st.columns(2)

        with a:

            start = st.date_input(
                "From",
                date.today().replace(day=1)
            ).isoformat()

        with b:

            end = st.date_input(
                "To",
                date.today()
            ).isoformat()

    sr = filt(
        sales,
        start,
        end
    )

    pr = filt(
        purchases,
        start,
        end
    )

    total_sales = sum(
        float(x["sales"])
        for x in sr
    )

    total_profit = sum(
        float(x["profit"])
        for x in sr
    )

    total_ingredients = sum(
        float(x["amount"])
        for x in pr
    )

    total_items = sum(
        int(x["quantity"])
        for x in sr
    )

    # REPORT METRICS

    cols = st.columns(4)

    report_metrics = [
        ("💰", "Sales", total_sales),
        ("📈", "Profit", total_profit),
        ("🛒", "Ingredients", total_ingredients),
        ("📦", "Items", total_items)
    ]

    for col, (
        icon,
        label,
        value
    ) in zip(
        cols,
        report_metrics
    ):

        with col:

            display = (
                money(value)
                if label != "Items"
                else f"{int(value):,}"
            )

            st.markdown(
                f"""
<div class="metric-card">

    <div class="metric-icon">
        {icon}
    </div>

    <div class="metric-label">
        {label}
    </div>

    <div class="metric-value">
        {display}
    </div>

</div>
""",
                unsafe_allow_html=True
            )

    # =====================================================
    # SALES
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Orders'
        '</div>',
        unsafe_allow_html=True
    )

    if not sr:

        st.markdown(
            """
<div class="empty">

    <div class="empty-icon">
        📭
    </div>

    No orders found for this period.

</div>
""",
            unsafe_allow_html=True
        )

    else:

        for r in sr:

            customer = (
                r.get("customer_name", "")
                or ""
            ).strip()

            details = (
                r.get("order_details", "")
                or ""
            ).strip()

            customer_display = (
                escape(customer)
                if customer
                else "No customer name"
            )

            details_display = (
                escape(details)
                if details
                else escape(
                    str(
                        r.get(
                            "product",
                            ""
                        )
                    )
                )
            )

            c1, c2 = st.columns(
                [7, 1]
            )

            with c1:

                st.markdown(
                    f"""
<div class="order-card">

    <div class="order-name">
        👤 {customer_display}
    </div>

    <div class="order-details">
        {details_display}
    </div>

    <div class="order-details">
        📅 {escape(str(r["date"])[:10])}
    </div>

    <div style="margin-top:10px;">

        <span class="order-price">
            {money(r["sales"])}
        </span>

        &nbsp;&nbsp;

        <span class="order-profit">
            +{money(r["profit"])} profit
        </span>

    </div>

</div>
""",
                    unsafe_allow_html=True
                )

            with c2:

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_{r['id']}",
                    use_container_width=True
                ):

                    sb.table("sales") \
                        .delete() \
                        .eq(
                            "id",
                            r["id"]
                        ) \
                        .execute()

                    st.rerun()

    # =====================================================
    # PURCHASES
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Ingredient purchases'
        '</div>',
        unsafe_allow_html=True
    )

    if pr:

        for r in pr:

            c1, c2, c3 = st.columns(
                [2, 5, 2]
            )

            with c1:

                st.caption(
                    str(r["date"])[:10]
                )

            with c2:

                st.write(
                    f"🛒 {r['item']}"
                )

            with c3:

                st.write(
                    f"**{money(r['amount'])}**"
                )

    else:

        st.info(
            "No ingredient purchases recorded."
        )

    # =====================================================
    # PRODUCTS
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Product reference'
        '</div>',
        unsafe_allow_html=True
    )

    product_rows = []

    for name, (
        price,
        profit
    ) in PRODUCTS.items():

        cost = price - profit

        product_rows.append({
            "Product": name,
            "Selling price": money(price),
            "Profit": money(profit),
            "Cost": money(cost)
        })

    # Do NOT use hide_index because older
    # Streamlit versions may not support it.

    st.dataframe(
        product_rows,
        use_container_width=True
    )

    # =====================================================
    # COMBOS
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Temporary combos'
        '</div>',
        unsafe_allow_html=True
    )

    combo_rows = []

    for name, (
        price,
        cost
    ) in COMBOS.items():

        combo_rows.append({
            "Combo": name,
            "Customer price": money(price),
            "Making cost": money(cost),
            "Profit": money(
                price - cost
            )
        })

    st.dataframe(
        combo_rows,
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
<div style="
    text-align:center;
    color:#aa9990;
    font-size:.72rem;
    padding-top:2rem;
">

    🍫 Brownie Book
    &nbsp;•&nbsp;
    Your business, your numbers.

</div>
""",
    unsafe_allow_html=True
)
