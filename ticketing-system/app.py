import os
from datetime import datetime
from typing import Optional

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from crud import (
    add_message,
    create_ticket,
    delete_ticket,
    get_all_tickets,
    get_ticket_by_id,
    get_ticket_messages,
    seed_sample_data,
    update_ticket_status,
)
from database import SessionLocal, engine
from models import Base, TicketStatus

st.set_page_config(page_title="Support Ticket System", page_icon="🎫", layout="wide")


def init_db() -> None:
    """Create database tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def refresh_app() -> None:
    """Force a UI refresh after CRUD operations."""
    st.rerun()


def format_datetime(dt: Optional[datetime]) -> str:
    if not dt:
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def sidebar_navigation() -> str:
    st.sidebar.title("🎫 Ticketing Menu")
    return st.sidebar.radio(
        "Go to",
        ["View Tickets", "Create Ticket", "Ticket Details", "Seed Sample Data"],
    )


def view_tickets_page() -> None:
    st.header("📋 All Tickets")
    with SessionLocal() as db:
        tickets = get_all_tickets(db)

    if not tickets:
        st.info("No tickets found.")
        return

    table_data = [
        {
            "Ticket ID": t.ticket_id,
            "Title": t.title,
            "Status": t.status.value,
            "Created By": t.created_by,
            "Created At": format_datetime(t.created_at),
        }
        for t in tickets
    ]
    st.dataframe(table_data, use_container_width=True)


def create_ticket_page() -> None:
    st.header("➕ Create Ticket")
    with st.form("create_ticket_form"):
        title = st.text_input("Title", max_chars=255)
        created_by = st.text_input("Created By", max_chars=100)
        submitted = st.form_submit_button("Create Ticket")

    if submitted:
        if not title.strip() or not created_by.strip():
            st.error("Title and Created By are required.")
            return

        try:
            with SessionLocal() as db:
                ticket = create_ticket(
                    db=db,
                    title=title.strip(),
                    created_by=created_by.strip(),
                )
            st.success(f"Ticket #{ticket.ticket_id} created successfully.")
            refresh_app()
        except SQLAlchemyError as e:
            st.error(f"Failed to create ticket: {e}")


def ticket_details_page() -> None:
    st.header("🔎 Ticket Details")
    with SessionLocal() as db:
        tickets = get_all_tickets(db)

        if not tickets:
            st.info("No tickets available.")
            return

        ticket_options = {f"#{t.ticket_id} - {t.title}": t.ticket_id for t in tickets}
        selected_label = st.selectbox("Select a Ticket", list(ticket_options.keys()))
        selected_ticket_id = ticket_options[selected_label]

        ticket = get_ticket_by_id(db, selected_ticket_id)
        if not ticket:
            st.error("Ticket not found.")
            return

        st.subheader(f"Ticket #{ticket.ticket_id}: {ticket.title}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Status", ticket.status.value)
        col2.metric("Created By", ticket.created_by)
        col3.metric("Created At", format_datetime(ticket.created_at))
        col4.metric("Messages", str(len(ticket.messages)))

        st.markdown("---")
        st.subheader("💬 Messages")
        messages = get_ticket_messages(db, selected_ticket_id)
        if not messages:
            st.info("No messages yet.")
        else:
            for m in messages:
                with st.container(border=True):
                    st.markdown(f"**{m.author}** • {format_datetime(m.created_at)}")
                    st.write(m.message_text)

        st.markdown("---")
        st.subheader("➕ Add Message")
        with st.form("add_message_form"):
            author = st.text_input("Author", max_chars=100)
            message_text = st.text_area("Message Text", max_chars=5000)
            add_msg_submitted = st.form_submit_button("Add Message")

        if add_msg_submitted:
            if not author.strip() or not message_text.strip():
                st.error("Author and Message Text are required.")
            else:
                try:
                    add_message(
                        db=db,
                        ticket_id=selected_ticket_id,
                        author=author.strip(),
                        message_text=message_text.strip(),
                    )
                    st.success("Message added successfully.")
                    refresh_app()
                except SQLAlchemyError as e:
                    st.error(f"Failed to add message: {e}")

        st.markdown("---")
        st.subheader("🔄 Update Status")
        with st.form("update_status_form"):
            new_status = st.selectbox(
                "Status",
                [s.value for s in TicketStatus],
                index=[s.value for s in TicketStatus].index(ticket.status.value),
            )
            update_status_submitted = st.form_submit_button("Update Status")

        if update_status_submitted:
            try:
                update_ticket_status(
                    db=db,
                    ticket_id=selected_ticket_id,
                    status=TicketStatus(new_status),
                )
                st.success("Status updated successfully.")
                refresh_app()
            except SQLAlchemyError as e:
                st.error(f"Failed to update status: {e}")

        st.markdown("---")
        st.subheader("🗑️ Delete Ticket")
        confirm_delete = st.checkbox("I confirm I want to delete this ticket and all related messages.")
        if st.button("Delete Ticket", type="primary"):
            if not confirm_delete:
                st.warning("Please confirm deletion first.")
            else:
                try:
                    deleted = delete_ticket(db=db, ticket_id=selected_ticket_id)
                    if deleted:
                        st.success("Ticket deleted successfully.")
                        refresh_app()
                    else:
                        st.error("Ticket not found.")
                except SQLAlchemyError as e:
                    st.error(f"Failed to delete ticket: {e}")


def seed_data_page() -> None:
    st.header("🌱 Seed Sample Data")
    st.write("This will insert 3 tickets and 2 messages per ticket if the database is empty.")
    if st.button("Seed Data"):
        try:
            with SessionLocal() as db:
                inserted = seed_sample_data(db)
            if inserted:
                st.success("Sample data seeded successfully.")
            else:
                st.info("Seed skipped: Tickets already exist.")
            refresh_app()
        except SQLAlchemyError as e:
            st.error(f"Failed to seed data: {e}")


def main() -> None:
    st.title("🎟️ Support Ticket System")
    st.caption("Streamlit + SQLAlchemy + PostgreSQL (Lakebase compatible)")

    if not os.getenv("DATABASE_URL"):
        st.error("DATABASE_URL is not set. Please set it in your environment.")
        st.stop()

    init_db()
    page = sidebar_navigation()

    if page == "View Tickets":
        view_tickets_page()
    elif page == "Create Ticket":
        create_ticket_page()
    elif page == "Ticket Details":
        ticket_details_page()
    elif page == "Seed Sample Data":
        seed_data_page()


if __name__ == "__main__":
    main()
