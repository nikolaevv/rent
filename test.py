import random
from matplotlib import pyplot as plt

def safe_devide(a, b):
    if b == 0:
        return 0

    return a / b

# Наша модель сервиса

all_debts = 0
debts_sums_1 = [0] * 900
days_1 = []

for i in range(100):
    debt = 0.0
    days_1 = []
    locked_summ = 0.0
    free_percent = 1
    paid_summ = 0.0
    rent = 30000.0
    rent_per_day = rent / 30
    balance = 100000.0
    debts = 0
    n = 3

    locked_summ += rent * n
    balance -= rent * n

    for j in range(900):
        # 1. расчёт процента свободной к снятию суммы
        paid_summ += rent_per_day
        free_summ = locked_summ - paid_summ
        free_percent = safe_devide(free_summ, locked_summ)

        debts_sums_1[j] = debt
        days_1.append(j + 1)

        # 2. Снятие денег при недостатке "подушки"
        if free_percent <= 0:
            locked_summ = 0
            
            if balance > rent_per_day * 90:
                balance -= rent_per_day
                free_percent = 1
                paid_summ = 0
                locked_summ = rent_per_day * 90
                debt = 0
            else:
                debt += rent_per_day
                debts += 1

        if free_percent > 0:
            # 3. снятие рандомной доступной суммы денег
            withdraw_summ = random.randint(0, int(locked_summ * 0.5 *free_percent))
            locked_summ -= withdraw_summ
            #paid_summ += withdraw_summ

        # 4. рандомный прирост прибыли
        profit = random.randint(0, int(withdraw_summ + 2 * rent_per_day))
        balance += profit

    all_debts += debts

all_debts_2 = 0
debts_sums_2 = [0] * 900
days_2 = []
# Текущая модель Аэропорта

for i in range(100):
    debt = 0.0
    days_2 = []
    rent = 30000.0
    rent_per_day = rent / 30
    balance = 100000.0
    debts = 0
    day = 0
    n = 3
    locked_summ = rent * n
    isActiveDebt = False

    for j in range(900):
        debts_sums_2[j] = debt
        days_2.append(j + 1)

        # 1. Снятие денег на 90й день


        if j % 90 == 0 or isActiveDebt:
            isActiveDebt = True

            if balance >= 1.3 * locked_summ:
                balance -= locked_summ
                isActiveDebt = False
                debt = 0
            else:
                debts += 1
                debt += rent_per_day
        
        # 2. рандомный прирост прибыли
        profit = random.randint(0, int(2 * rent_per_day))
        balance += profit

    all_debts_2 += debts

for i in range(len(days_1)):
    days_1[i] = days_1[i] / 100

for i in range(len(days_2)):
    days_2[i] = days_2[i] / 100

print("Среднее количество дней наличия дебетовой задолженности за 3 года")
print("Rent =", all_debts / 100)
print("Текущее решение =", all_debts_2 / 100)

print(len(days_2))
ax = plt.gca()
ax.plot(days_1, debts_sums_1, label='Rent')
ax.plot(days_2, debts_sums_2, label='Default')
#ax.plot(fib_base, days_1, label='days')


ax.set_title('Сумма дебиторской задолженности')
ax.set_xlabel('Номер дня')
ax.set_ylabel('Сумма в рублях')

ax.legend()
plt.show()