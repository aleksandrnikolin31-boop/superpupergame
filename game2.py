
import streamlit as st

st.set_page_config(
    page_title="DOOM: Адский Тир", page_icon="🎯", layout="centered"
)

st.title("👹 DOOM: Адский Тир")
st.write(
    "Здесь нужно **целиться и стрелять кликом мышки**! Уничтожайте демонов"
    " до того, как они нанесут урон. Не тратьте патроны впустую!"
)

# HTML5 Canvas + JS для игры на меткость и скорость кликов
aim_shooter_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            background-color: #0d0e12;
            font-family: 'Courier New', Courier, monospace;
            user-select: none;
        }
        #canvas-container {
            position: relative;
            box-shadow: 0px 0px 35px rgba(255, 0, 0, 0.5);
            border: 2px solid #ff3333;
            border-radius: 8px;
            overflow: hidden;
            cursor: crosshair; /* Прицел вместо курсора */
        }
        canvas {
            background: linear-gradient(to bottom, #14141f, #07070a);
            display: block;
        }
        .btn-restart {
            margin-top: 15px;
            padding: 12px 30px;
            font-size: 18px;
            background: linear-gradient(45deg, #ff2a2a, #ff6b6b);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4);
        }
        #ui-layer {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #ff3333;
            font-size: 26px;
            font-weight: bold;
            display: none;
            background: rgba(0,0,0,0.9);
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #ff3333;
            width: 75%;
        }
    </style>
</head>
<body>

<div id="canvas-container">
    <canvas id="aimCanvas" width="500" height="400"></canvas>
    <div id="ui-layer">
        <span id="death-reason">💀 ВЫ ПОГИБЛИ!</span><br>
        <div id="final-score" style="color:#fff; font-size:18px; margin: 15px 0;"></div>
        <button class="btn-restart" onclick="resetGame()">В БОЙ 🔄</button>
    </div>
</div>

<script>
    const canvas = document.getElementById("aimCanvas");
    const ctx = canvas.getContext("2d");
    const uiLayer = document.getElementById("ui-layer");
    const finalScoreDiv = document.getElementById("final-score");
    const deathReasonSpan = document.getElementById("death-reason");

    // Состояние игры
    let hp = 100;
    let ammo = 30;
    let score = 0;
    let targets = [];
    let gameOver = false;
    let spawnTimer = 0;
    let gameTicks = 0;

    // Виды демонов
    const DEMON_TYPES = [
        { emoji: "🐒", size: 35, hp: 1, points: 10, lifetime: 120, label: "Имп" },
        { emoji: "👁️", size: 40, hp: 1, points: 25, lifetime: 90, label: "Какодемон" },
        { emoji: "👹", size: 55, hp: 3, points: 100, lifetime: 150, label: "КИБЕРДЕМОН" } // Требует 3 клика!
    ];

    // Клик мышкой (Выстрел)
    canvas.addEventListener("mousedown", function(event) {
        if (gameOver) return;

        const rect = canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        if (ammo <= 0) return;
        ammo--; // Тратим патрон

        let hitSomething = false;

        // Проверяем попадание по демонам (с конца массива, чтобы кликать по верхним)
        for (let i = targets.length - 1; i >= 0; i--) {
            let t = targets[i];
            // Считаем расстояние от центра эмодзи
            let dist = Math.hypot(mouseX - (t.x + t.size/2), mouseY - (t.y + t.size/2));
            
            if (dist < t.size / 1.3) {
                t.hp--;
                hitSomething = true;
                
                // Вспышка попадания
                ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                if (t.hp <= 0) {
                    score += t.points;
                    // Даем бонусные патроны за Кибердемона или просто за везение
                    if (t.emoji === "👹") ammo += 5;
                    else if (Math.random() < 0.3) ammo += 2;
                    
                    targets.splice(i, 1);
                }
                break; // Попали в одного, пуля дальше не летит
            }
        }

        // Проверка на конец патронов
        if (ammo <= 0 && targets.length === 0) {
            checkGameOver();
        }
    });

    function spawnDemon() {
        // Шанс появления Кибердемона растет со счетом
        let rand = Math.random();
        let type;
        if (rand < 0.15 && score > 150) type = DEMON_TYPES[2]; // Кибердемон
        else if (rand < 0.45) type = DEMON_TYPES[1];          // Какодемон
        else type = DEMON_TYPES[0];                           // Имп

        let margin = 60;
        let x = margin + Math.random() * (canvas.width - margin * 2 - type.size);
        let y = margin + Math.random() * (canvas.height - margin * 2 - type.size);

        targets.push({
            emoji: type.emoji,
            size: type.size,
            hp: type.hp,
            maxHp: type.hp,
            points: type.points,
            x: x,
            y: y,
            maxLife: type.lifetime,
            life: type.lifetime
        });
    }

    function update() {
        if (gameOver) return;

        gameTicks++;
        
        // Частота появления демонов увеличивается со временем
        spawnTimer++;
        let spawnRate = Math.max(20, 60 - Math.floor(score / 20));
        if (spawnTimer >= spawnRate) {
            spawnDemon();
            spawnTimer = 0;
        }

        // Уменьшаем время жизни демонов
        for (let i = targets.length - 1; i >= 0; i--) {
            targets[i].life--;
            
            // Если не успели кликнуть, демон кусает игрока и исчезает
            if (targets[i].life <= 0) {
                let damage = targets[i].emoji === "👹" ? 30 : 15;
                hp -= damage;
                targets.splice(i, 1);
            }
        }

        checkGameOver();
    }

    function checkGameOver() {
        if (hp <= 0) {
            endGame("💀 ДЕМОНЫ РАЗОРВАЛИ ВАС!");
        } else if (ammo <= 0 && targets.length === 0) {
            endGame("🚫 ЗАКОНЧИЛИСЬ ПАТРОНЫ!");
        }
    }

    function endGame(reason) {
        gameOver = true;
        deathReasonSpan.innerText = reason;
        finalScoreDiv.innerText = "Истреблено на очки: " + score;
        uiLayer.style.display = "block";
    }

    function resetGame() {
        hp = 100;
        ammo = 35;
        score = 0;
        targets = [];
        gameOver = false;
        spawnTimer = 0;
        uiLayer.style.display = "none";
        loop();
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Рисуем сетку прицела на фоне для атмосферы
        ctx.strokeStyle = "rgba(255, 0, 0, 0.1)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(canvas.width/2, 0); ctx.lineTo(canvas.width/2, canvas.height);
        ctx.moveTo(0, canvas.height/2); ctx.lineTo(canvas.width, canvas.height/2);
        ctx.stroke();

        // Рисуем демонов
        targets.forEach(t => {
            // Шкала времени жизни (кружок вокруг или полоска под ним)
            ctx.fillStyle = "rgba(255, 0, 0, 0.3)";
            let lifeWidth = (t.life / t.maxLife) * t.size;
            ctx.fillRect(t.x, t.y + t.size + 4, lifeWidth, 4);

            // Если у демона много HP (Кибердемон), рисуем полоску здоровья
            if (t.maxHp > 1) {
                ctx.fillStyle = "#00ff00";
                let hpWidth = (t.hp / t.maxHp) * t.size;
                ctx.fillRect(t.x, t.y - 8, hpWidth, 4);
            }

            // Рисуем самого демона
            ctx.font = t.size + "px Arial";
            ctx.textAlign = "left";
            ctx.textBaseline = "top";
            ctx.fillText(t.emoji, t.x, t.y);
        });

        // Верхний интерфейс (Инфо-панель)
        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(0, 0, canvas.width, 40);

        ctx.fillStyle = "#ff3333";
        ctx.font = "bold 14px 'Courier New'";
        ctx.textAlign = "left";
        ctx.fillText("❤️ HP: " + hp + "%", 15, 15);

        ctx.fillStyle = "#00ffcc";
        ctx.fillText("🎒 ПАТРОНЫ: " + ammo, 160, 15);

        ctx.fillStyle = "#fff";
        ctx.textAlign = "right";
        ctx.fillText("СЧЕТ: " + score, canvas.width - 15, 15);
    }

    function loop() {
        update();
        draw();
        if (!gameOver) {
            requestAnimationFrame(loop);
        }
    }

    resetGame();
</script>

</body>
</html>
"""

st.components.v1.html(aim_shooter_html, height=460)
