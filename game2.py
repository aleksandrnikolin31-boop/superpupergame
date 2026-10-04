import random
import streamlit as st

st.set_page_config(page_title="DOOM: Streamlit Edition", page_icon="👹")

st.title("👹 DOOM: Текстовый Ад")
st.write(
    "Вы — космический десантник на заброшенной базе. Зачистите этажи от"
    " демонов!"
)

# 1. Инициализация состояния игры
if "player" not in st.session_state:
  st.session_state.player = {
      "hp": 100,
      "armor": 50,
      "ammo": 20,
      "weapon": "Пистолет 🔫",
      "floor": 1,
      "kills": 0,
  }
  st.session_state.enemy = None
  st.session_state.log = [
      "Вы прибыли на первый этаж комплекса. Здесь пахнет серой..."
  ]
  st.session_state.game_over = False


# Функция для добавления записей в боевой журнал
def add_log(text):
  st.session_state.log.insert(0, text)


# Функция перезапуска
def restart():
  st.session_state.clear()
  st.rerun()


p = st.session_state.player

# 2. Проверка экрана смерти
if st.session_state.game_over or p["hp"] <= 0:
  st.error(f"💀 ВЫ ПОГИБЛИ! Демоны разорвали вас на этаже {p['floor']}.")
  st.metric("Уничтожено демонов", p["kills"])
  st.button("Возродиться в контрольной точке 🔄", on_click=restart)

else:
  # Появление нового врага, если его нет
  if st.session_state.enemy is None:
    enemy_types = [
        {"name": "Имп 🐒", "hp": 30, "damage": 8},
        {"name": "Пинки 🐖", "hp": 50, "damage": 15},
        {"name": "Какодемон 👁️", "hp": 80, "damage": 20},
    ]
    # На высоких этажах враги сильнее
    base_enemy = random.choice(enemy_types)
    st.session_state.enemy = {
        "name": base_enemy["name"],
        "hp": base_enemy["hp"] + (p["floor"] * 5),
        "damage": base_enemy["damage"] + p["floor"],
    }
    add_log(f"🚨 Из темноты выпрыгнул **{st.session_state.enemy['name']}**!")

  e = st.session_state.enemy

  # 3. Интерфейс (Характеристики игрока и врага)
  col1, col2, col3 = st.columns(3)
  with col1:
    st.subheader("Состояние бойца")
    st.write(f"❤️ Здоровье: **{p['hp']}%**")
    st.write(f"🛡️ Броня: **{p['armor']}%**")
    st.write(f"🎒 Патроны: **{p['ammo']}**")
    st.write(f"⚔️ Оружие: **{p['weapon']}**")
  with col2:
    st.subheader("Прогресс")
    st.write(f"🪜 Этаж: **{p['floor']}**")
    st.write(f"🎯 Убито врагов: **{p['kills']}**")
  with col3:
    st.subheader("Противник")
    st.write(f"👾 Имя: **{e['name']}**")
    st.write(f"🩸 Жизнь монстра: **{e['hp']}**")

  st.write("---")

  # 4. Кнопки действий (Логика боя) — ТУТ ВСЁ ИСПРАВЛЕНО
  action_cols = st.columns(3)

  with action_cols[0]:
    # Кнопка АТАКА
    if st.button("🔥 ОГОНЬ!", use_container_width=True):
      if p["ammo"] > 0:
        p["ammo"] -= 1
        damage = (
            random.randint(15, 30)
            if "Дробовик" in p["weapon"]
            else random.randint(8, 15)
        )
        e["hp"] -= damage
        add_log(f"Вы выстрелили в {e['name']} и нанесли **{damage}** урона.")

        if e["hp"] <= 0:
          add_log(f"🎉 Вы уничтожили {e['name']}!")
          p["kills"] += 1
          st.session_state.enemy = None

          loot_roll = random.random()
          if loot_roll < 0.3:
            p["weapon"] = "Двуствольный Дробовик 🪓"
            add_log("💥 О ДА! Вы нашли ДРОБОВИК!")
          elif loot_roll < 0.6:
            p["ammo"] += 10
            add_log("📦 Найдена коробка с патронами (+10).")
          else:
            p["hp"] = min(100, p["hp"] + 20)
            add_log("🧪 Найдена аптечка (+20 HP).")

          p["floor"] += 1
          st.rerun()
      else:
        add_log("⛔ ЩЕЛК! Патроны закончились!")

  with action_cols[1]:
    # Кнопка БЛИЖНИЙ БОЙ (Бензопила)
    if st.button("🪚 Бензопила", use_container_width=True):
      damage = random.randint(5, 12)
      e["hp"] -= damage
      p["ammo"] += 3
      add_log(
          f"Вы распилили врага на **{damage}** урона и добыли **3** патрона!"
      )

      if e["hp"] <= 0:
        add_log(f"🎉 {e['name']} распилен на куски!")
        p["kills"] += 1
        st.session_state.enemy = None
        p["floor"] += 1
        st.rerun()

  with action_cols[2]:
    # Кнопка ПОИСК БРОНИ
    if st.button("🏃 Маневр уклонения", use_container_width=True):
      p["armor"] = min(100, p["armor"] + 15)
      add_log("Вы заняли укрытие и укрепили броню (+15% 🛡️).")

  # Ответный ход монстра (если он выжил)
  if st.session_state.enemy is not None and st.session_state.enemy["hp"] > 0:
    if random.random() < 0.7:
      e_damage = random.randint(5, e["damage"])
      if p["armor"] > 0:
        p["armor"] -= int(e_damage * 0.5)
        p["hp"] -= int(e_damage * 0.5)
        if p["armor"] < 0:
          p["armor"] = 0
      else:
        p["hp"] -= e_damage
      add_log(f"💥 {e['name']} атаковал вас и нанес **{e_damage}** урона!")

  # 5. Вывод боевого журнала
  st.write("---")
  st.subheader("Журнал боя:")
  for log_entry in st.session_state.log[:5]:
    st.write(log_entry)
