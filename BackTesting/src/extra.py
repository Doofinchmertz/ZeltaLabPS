if self.assets == 0 and self.cash <= 0:
    print(f"Game Over at timestamp : {timestamp}")
    exit()

if self.assets == 0 and self.cash > 0:
    if signal == 1:
        self.assets += self.cash/price
        self.cash = 0
    if signal == -1:
        self.assets -= self.cash/price
        self.cash *= 2

if self.assets > 0 and self.cash <= 0:
    if signal == 1:
        print(f"Invalid Trade at timestamp : {timestamp}")
    if signal == -1:
        self.cash += self.assets*price
        self.assets = 0

if self.assets > 0 and self.cash > 0:
    if signal == 1:
        self.assets += self.cash/price
        self.cash = 0
    if signal == -1:
        self.cash += self.assets*price
        self.assets = 0

if self.assets < 0 and self.cash > 0:
    if signal == 1:
        self.cash -= self.assets*price
        self.assets = 0
    if signal == -1:
        self.assets -= self.cash/price
        self.cash *= 2

if self.assets < 0 and self.cash <= 0:
    if signal == 1:
        self.cash -= self.assets*price
        self.assets = 0
    if signal == -1:
        print(f"Invalid Trade at timestamp : {timestamp}")