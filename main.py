import json
import os
from datetime import datetime, timedelta

# Файл для хранения данных
DATA_FILE = "goals.json"

class Goal:
    """Класс для представления финансовой цели (п. 1.1)"""
    def __init__(self, name, target_amount, category, deadline=None):
        self.name = name
        self.target_amount = target_amount
        self.current_balance = 0
        self.category = category
        self.status = "в процессе"
        self.deadline = deadline # Формат: YYYY-MM-DD (п. повышенный уровень)
        self.created_at = datetime.now().strftime("%Y-%m-%d")

    def add_funds(self, amount):
        """Увеличение баланса с проверкой на превышение (п. 1.2)"""
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть больше нуля.")
        
        if self.current_balance + amount > self.target_amount:
            print(f"⚠️ Внимание: Сумма превышает итоговую цель. Баланс будет установлен на максимум ({self.target_amount}).")
            self.current_balance = self.target_amount
        else:
            self.current_balance += amount
        
        self.update_status() # (п. 1.4)
        self.check_notifications() # (Доп. функция)

    def withdraw_funds(self, amount):
        """Уменьшение баланса (п. 1.2)"""
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть больше нуля.")
        if amount > self.current_balance:
            raise ValueError("Недостаточно средств на балансе цели.")
        
        self.current_balance -= amount
        self.status = "в процессе" # Если сняли деньги, цель снова в процессе
        print(f"Снято {amount} руб. Текущий баланс: {self.current_balance}")

    def get_progress(self):
        """Вычисление процента выполнения (п. 1.3)"""
        if self.target_amount == 0:
            return 100.0
        return round((self.current_balance / self.target_amount) * 100, 2)

    def update_status(self):
        """Обновление статуса при достижении цели (п. 1.4)"""
        if self.current_balance >= self.target_amount:
            self.status = "выполнена"
            print(f"🎉 Поздравляем! Цель '{self.name}' полностью достигнута!")

    def check_notifications(self):
        """Уведомления о достижении определенного процента (Доп. функция)"""
        progress = self.get_progress()
        if progress >= 50 and progress < 100:
            print(f"🔔 Уведомление: Вы накопили уже {progress}% на цель '{self.name}'!")

    def estimate_completion_date(self):
        """Предложение даты завершения (Повышенный уровень)"""
        if self.current_balance == 0 or self.status == "выполнена":
            return "Недостаточно данных или цель уже выполнена"
        
        # Простой расчет: предполагаем, что скорость накопления останется такой же
        # Вычисляем, сколько в среднем копится в день с момента создания
        created_date = datetime.strptime(self.created_at, "%Y-%m-%d")
        days_passed = (datetime.now() - created_date).days
        
        if days_passed == 0:
            return "Копите первый день, прогноз невозможен."
        
        avg_daily_save = self.current_balance / days_passed
        remaining_amount = self.target_amount - self.current_balance
        
        if avg_daily_save <= 0:
            return "Неизвестно"
            
        days_needed = int(remaining_amount / avg_daily_save)
        estimated_date = datetime.now() + timedelta(days=days_needed)
        return estimated_date.strftime("%Y-%m-%d")

    def to_dict(self):
        """Преобразование объекта в словарь для сохранения в JSON"""
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_balance": self.current_balance,
            "category": self.category,
            "status": self.status,
            "deadline": self.deadline,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Создание объекта из словаря при загрузке из JSON"""
        goal = cls(data["name"], data["target_amount"], data["category"], data.get("deadline"))
        goal.current_balance = data["current_balance"]
        goal.status = data["status"]
        goal.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d"))
        return goal


class PiggyBankApp:
    """Основной класс приложения"""
    def __init__(self):
        self.goals = []
        self.load_data()

    def load_data(self):
        """Загрузка данных из JSON (Рекомендации)"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.goals = [Goal.from_dict(g) for g in data]
            except Exception as e:
                print(f"Ошибка при чтении файла: {e}")
                self.goals = []

    def save_data(self):
        """Сохранение данных в JSON (Рекомендации)"""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([goal.to_dict() for goal in self.goals], f, ensure_ascii=False, indent=4)

    def add_goal(self):
        """Добавление цели (п. 1.1)"""
        print("\n--- Добавление новой цели ---")
        name = input("Название цели: ").strip()
        
        try:
            target_amount = float(input("Итоговая сумма: "))
            if target_amount <= 0:
                raise ValueError("Сумма должна быть больше нуля.")
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
            return

        categories = ["Работа", "Здоровье", "Отдых", "Покупки", "Образование", "Другое"]
        print(f"Доступные категории: {', '.join(categories)}")
        category = input("Категория: ").strip().capitalize()
        
        # Обработка даты дедлайна (Повышенный уровень)
        deadline_str = input("Дедлайн (ГГГГ-ММ-ДД, оставьте пустым если нет): ").strip()
        deadline = None
        if deadline_str:
            try:
                datetime.strptime(deadline_str, "%Y-%m-%d")
                deadline = deadline_str
            except ValueError:
                print("⚠️ Неверный формат даты. Дедлайн не установлен.")

        new_goal = Goal(name, target_amount, category, deadline)
        self.goals.append(new_goal)
        self.save_data()
        print(f"✅ Цель '{name}' успешно добавлена!")

    def show_goals(self):
        """Просмотр прогресса и категорий (п. 1.3, 1.5)"""
        if not self.goals:
            print("\nСписок целей пуст.")
            return

        print("\n--- Ваши цели ---")
        for idx, goal in enumerate(self.goals, 1):
            progress = goal.get_progress()
            est_date = goal.estimate_completion_date()
            
            print(f"{idx}. [{goal.category}] {goal.name}")
            print(f"   Статус: {goal.status.upper()}")
            print(f"   Баланс: {goal.current_balance} / {goal.target_amount} руб. ({progress}%)")
            
            if goal.deadline:
                # Напоминание о дедлайне (Повышенный уровень)
                days_left = (datetime.strptime(goal.deadline, "%Y-%m-%d") - datetime.now()).days
                if days_left < 0 and goal.status != "выполнена":
                    print(f"   🔴 ВНИМАНИЕ: Дедлайн прошел {abs(days_left)} дней назад!")
                else:
                    print(f"   ⏳ Дедлайн: {goal.deadline} (осталось дней: {days_left})")
            
            if goal.status != "выполнена":
                print(f"   📅 Прогноз завершения (при текущем темпе): {est_date}")
            print("-" * 30)

    def manage_balance(self):
        """Изменение баланса цели (п. 1.2)"""
        if not self.goals:
            print("\nСписок целей пуст.")
            return
            
        self.show_goals()
        try:
            idx = int(input("Выберите номер цели для операции: ")) - 1
            if idx < 0 or idx >= len(self.goals):
                raise IndexError
            goal = self.goals[idx]
        except (ValueError, IndexError):
            print("❌ Неверный номер цели.")
            return

        action = input("1. Пополнить\n2. Снять\nВыберите действие: ")
        try:
            amount = float(input("Введите сумму: "))
            if action == "1":
                goal.add_funds(amount)
            elif action == "2":
                goal.withdraw_funds(amount)
            else:
                print("Неверное действие.")
                return
            self.save_data()
        except ValueError as e:
            print(f"❌ Ошибка: {e}")

    def delete_goal(self):
        """Удаление цели (п. 1.6)"""
        if not self.goals:
            print("\nСписок целей пуст.")
            return
            
        self.show_goals()
        try:
            idx = int(input("Введите номер цели для удаления: ")) - 1
            if idx < 0 or idx >= len(self.goals):
                raise IndexError
            deleted_goal = self.goals.pop(idx)
            self.save_data()
            print(f"🗑️ Цель '{deleted_goal.name}' удалена.")
        except (ValueError, IndexError):
            print("❌ Неверный номер цели.")

    def show_total_progress(self):
        """Общий прогресс по всем целям (Дополнительная функция)"""
        if not self.goals:
            print("\nНет целей для подсчета.")
            return
        
        total_target = sum(g.target_amount for g in self.goals)
        total_saved = sum(g.current_balance for g in self.goals)
        
        if total_target == 0:
            print("Общая сумма целей равна нулю.")
            return
            
        overall_progress = round((total_saved / total_target) * 100, 2)
        print("\n--- Общий прогресс ---")
        print(f"Всего накоплено: {total_saved} из {total_target} руб.")
        print(f"Общий прогресс: {overall_progress}%")

    def run(self):
        """Главный цикл программы"""
        while True:
            print("\n=== КОПИЛКА ===")
            print("1. Добавить цель")
            print("2. Посмотреть цели")
            print("3. Пополнить/Снять средства")
            print("4. Удалить цель")
            print("5. Общий прогресс")
            print("0. Выход")
            
            choice = input("Выберите действие: ").strip()
            
            if choice == "1":
                self.add_goal()
            elif choice == "2":
                self.show_goals()
            elif choice == "3":
                self.manage_balance()
            elif choice == "4":
                self.delete_goal()
            elif choice == "5":
                self.show_total_progress()
            elif choice == "0":
                print("До свидания! Данные сохранены.")
                break
            else:
                print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    app = PiggyBankApp()
    app.run()