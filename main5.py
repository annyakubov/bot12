import logging
import pickle  #!!!!!
from datetime import datetime, timedelta


from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler
import atexit



DATA_FILE = "expenses_data.pkl"


categories = ['Food', 'Transportation', 'Entertainment']
expenses = {}

incomes = {}  #  новий словник для збереження доходів


TOKEN_BOT = "6042142412:AAEvIFZRDWYk8rsfkan9cijJsGH-WWzorFI"
user_data = dict()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)




async def start(update: Update, context: CallbackContext) -> None:
    logging.info("Command start was triggered")
    await update.message.reply_text(
        "Hello! I'm your income and expenses bot. What do you want to do?\n"
        "Commands :\n"
        "Adding tasks: /add_ex | \n"
        "Adding tasks: /add_income | \n"
        "View_all_ex tasks: /view_all_ex| \n"
        "View_monthly_ex tasks: /view_monthly_ex| \n"
        "View_weekly_ex tasks: /view_weekly_ex| \n"

        "Remove task:/remove <task number>\n"
        "View_stats tasks: /view_stats| \n"
    )


async def add_ex(update: Update, context: CallbackContext, ex_category=None) -> None:
    logging.info("command run <add_ex>")

    """
    Format add add_ex command
    /add_ex |
    """


    ex_amount = "".join(context.args).split("|")
    ex_food = ex_amount[0].strip()
    expen = ex_amount[1].strip()
    current_time = datetime.now().strftime ('%Y-%m-%d')  # вичесляє автоматично час
    await update.message.reply_text(f"Current time: {current_time}")


    if ex_food not in categories:
        await update.message.reply_text("Invalid category")

        return

    if ex_food not in expenses:
        expenses[ex_food] = []

    await update.message.reply_text(f"Available categories: {categories}")  # 3  повернення списку категорій

    new_expense = {"amount": expen, "date": current_time}

    expenses[ex_food].append(new_expense)


    await update.message.reply_text(f"Amount {ex_food} {ex_amount} {current_time} appended successfully")

    print(expenses)
    await update.message.reply_text(f"Expenses {ex_food} {expen} append successfully")


async def add_income(update: Update, context: CallbackContext) -> None:   #????????
    logging.info("command run <add_income>")

    income_args = "".join(context.args).split("|")
    income_category = income_args[0].strip()
    income_value = income_args[1].strip()
    current_time = datetime.now().strftime('%Y-%m-%d')

    await update.message.reply_text(f"Current time: {current_time}")

    # Додавання доходу до incomes
    new_income = {"amount": income_value, "date": current_time}

    if income_category not in incomes:
        incomes[income_category] = []

    incomes[income_category].append(new_income)

    await update.message.reply_text(f"Income {income_category} {income_value} {current_time} appended successfully")




async def view_all_ex(update: Update, context: CallbackContext, ) -> None:
    logging.info("command run <view_all_ex>")

    all_ex = "Ability to view all expenses,"
    for category, expenses_list in expenses.items():
        for expense in expenses_list:
            all_ex += f"{category}: {expense}\n"
    await update.message.reply_text(all_ex)


async def view_monthly_ex(update: Update, context: CallbackContext) -> None:
    logging.info("command run <view_monthly_ex>")

    current_month = datetime.now().month
    all_ex = "Expenses for the current month:\n"

    for category, expenses_list in expenses.items():
        for expense in expenses_list:
            if not isinstance(expense, dict):
                logging.warning(f"Invalid expense format: {expense}")
                continue

            expense_date_str = expense.get("date")
            if not expense_date_str:
                logging.warning(f"Missing 'date' in expense: {expense}")
                continue

            try:
                expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
                if expense_date.month == current_month:
                    all_ex += f"{category}: {expense['amount']} грн. ({expense_date_str})\n"
            except ValueError:
                logging.warning(f"Error while parsing date: {expense_date_str}")

    if not all_ex:
        all_ex = "No expenses for the current month."

    await update.message.reply_text(all_ex)


async def view_weekly_ex(update: Update, context: CallbackContext) -> None:
    logging.info("command run <view_weekly_ex>")

    current_date = datetime.now().date()
    week_ago_date = current_date - timedelta(weeks=1)

    all_ex = "Expenses for the last week:\n"
    for category, expenses_list in expenses.items():
        for expense in expenses_list:
            if not isinstance(expense, dict):
                logging.warning(f"Invalid expense format: {expense}")
                continue

            expense_date_str = expense.get("date")
            if not expense_date_str:
                logging.warning(f"Missing 'date' in expense: {expense}")
                continue

            try:
                expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
                if week_ago_date <= expense_date <= current_date:
                    all_ex += f"{category}: {expense['amount']} грн. ({expense_date_str})\n"
            except ValueError:
                logging.warning(f"Error while parsing date: {expense_date_str}")

    if not all_ex:
        all_ex = "No expenses for the last week."

    await update.message.reply_text(all_ex)


async def remove_ex(update: Update, context: CallbackContext) -> None:
    logging.info("command run <remove_ex>")

    if len(context.args) < 2:
        await update.message.reply_text("Please provide the category and amount of the expense/income you want to remove. Example: /remove_ex Food 50")
        return

    ex_amount = "".join(context.args).split("|")
    ex_category = ex_amount[0].strip()
    ex_value = ex_amount[1].strip()

    if ex_category not in categories:
        await update.message.reply_text("Invalid category")
        return

    if ex_category not in expenses:
        await update.message.reply_text("Category not found")
        return


    await update.message.reply_text(f"Removed {ex_category} {ex_value} successfully.")


async def view_stats(update: Update, context: CallbackContext) -> None:
    logging.info("command run <view_stats>")

    ex_args = "".join(context.args).split("|")
    ex_category = ex_args[0].strip()
    time_period = ex_args[1].strip().lower()

    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide the category and the time period (day/month/week/year) for which you want to view the statistics. Example: /view_stats Food|month")
        return

    # Визначення потрібної дати для відображення статистики
    selected_date = ...

    all_stats = ""

    # Опрацьовуємо витрати
    if ex_category in expenses:
        total_expenses = 0
        for expense in expenses[ex_category]:
            expense_date_str = expense.get("date")
            if expense_date_str:
                try:
                    expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
                    if expense_date >= selected_date:
                        total_expenses += int(expense['amount'])
                except ValueError:
                    logging.warning(f"Error while parsing date: {expense_date_str}")

        all_stats += f"Total {ex_category} expenses: {total_expenses} грн.\n"

    # Опрацьовуємо доходи
    if ex_category in incomes:
        total_incomes = 0
        for income in incomes[ex_category]:
            income_date_str = income.get("date")
            if income_date_str:
                try:
                    income_date = datetime.strptime(income_date_str, '%Y-%m-%d').date()
                    if income_date >= selected_date:
                        total_incomes += int(income['amount'])
                except ValueError:
                    logging.warning(f"Error while parsing date: {income_date_str}")

        all_stats += f"Total {ex_category} incomes: {total_incomes} грн."

    await update.message.reply_text(all_stats)





def save_data():
    with open(DATA_FILE, "wb") as file:
        pickle.dump(expenses, file)

def load_data():
    try:
        with open(DATA_FILE, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}


def run():
    global expenses
    expenses = load_data()

    app = ApplicationBuilder().token(TOKEN_BOT).build()
    logging.info("Application build successfully!")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler('add_ex', add_ex))
    app.add_handler(CommandHandler('add_income', add_income))
    app.add_handler(CommandHandler("view_all_ex", view_all_ex))
    app.add_handler(CommandHandler("view_monthly_ex", view_monthly_ex))
    app.add_handler(CommandHandler("view_weekly_ex", view_weekly_ex))
    app.add_handler(CommandHandler("remove_ex", remove_ex))
    app.add_handler(CommandHandler("view_stats", view_stats))


    # Регистрируем функцию сохранения данных перед завершением программы
    atexit.register(save_data)

    app.run_polling()

if __name__ == "__main__":
    run()
