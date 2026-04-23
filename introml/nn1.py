from math import exp, sqrt
from random import random, seed
seed(0)

def sigmoid(x):
    return 1 / (1 + exp(-x))

# 入力 nin個、出力 nout個のレイヤーを定義する。
class Layer:
    def __init__(self, nin, nout):
        self.nin = nin
        self.nout = nout
        # 重み・バイアスを初期化する。
        self.w = [ [ random()-0.5 for j in range(self.nin) ] for i in range(self.nout) ]
        self.b = [ random()-0.5 for i in range(self.nout) ]
        # 計算用の変数を初期化する。
        self.x = self.y = None
        self.dw = [ [ 0 for j in range(self.nin) ] for i in range(self.nout) ]
        self.db = [ 0 for i in range(self.nout) ]
        self.loss = 0
        return

    def __repr__(self):
        return f'<Layer {self.nin} x {self.nout}>'

    def forward(self, x):
        assert len(x) == self.nin, x
        # xは nin個の要素をもつ入力値のリスト。
        # 与えられた入力に対する各ノードの出力を計算する。
        self.x = x
        self.y = [
            sigmoid(sum( w1*x1 for (w1,x1) in zip(w, x) ) + b)
            for (w,b) in zip(self.w, self.b)
        ]
        # yは nout個の要素をもつ出力値のリスト
        return self.y

    def mse_loss(self, ya):
        assert len(ya) == len(self.y)
        # 与えられた正解に対する損失を求める。
        self.loss += sum( (y1-ya1)**2 for (y1,ya1) in zip(self.y, ya) )
        # 損失関数の微分を計算する。
        delta = [ 2*(y1-ya1) for (y1,ya1) in zip(self.y, ya) ]
        return delta

    def backward(self, delta):
        assert len(delta) == len(self.y)
        # self.y が計算されたときのシグモイド関数の微分を求める。
        ds = [ y1*(1-y1) for y1 in self.y ]
        # 各偏微分を計算する。
        for i in range(self.nout):
            for j in range(self.nin):
                self.dw[i][j] += delta[i] * ds[i] * self.x[j]
        for i in range(self.nout):
            self.db[i] += delta[i] * ds[i]
        # 各入力値の微分を求める。
        dx = [
            sum( delta[j]*ds[j]*self.w[j][i] for j in range(self.nout) )
            for i in range(self.nin)
        ]
        return dx

    def update(self, alpha):
        # 現在の勾配をもとに、損失が減る方向へ重み・バイアスを変化させる。
        for i in range(self.nout):
            for j in range(self.nin):
                self.w[i][j] -= alpha * self.dw[i][j]
        for i in range(self.nout):
            self.b[i] -= alpha * self.db[i]
        # 計算用の変数をクリアしておく。
        for i in range(self.nout):
            for j in range(self.nin):
                self.dw[i][j] = 0
        for i in range(self.nout):
            self.db[i] = 0
        self.loss = 0
        return

DAYS = [31,28,31,30,31,30,31,31,30,31,30,31]
def main():
    layer1 = Layer(2, 20)
    layer2 = Layer(layer1.nout, 20)
    layer3 = Layer(layer2.nout, 1)
    layers = [layer1, layer2, layer3]
    alpha = 0.01
    N = 1000
    # 繰り返す。
    for i in range(N):
        # 100個分のランダムな訓練データを作成する。
        data = []
        for j in range(100):
            year = int(random()*100)
            month = int(random()*12)
            days = DAYS[month]
            if year % 4 == 0 and month == 1:
                days += 1
            x = [ year/100.0, month/12.0 ]
            ya = [ (days-28)/3.0 ]
            data.append((x,ya))
        for (x,ya) in data:
            # 入力に対する出力を計算する。
            y = x
            for layer in layers:
                y = layer.forward(y)
            # 損失を計算する。
            delta = layers[-1].mse_loss(ya)
            # 勾配を計算。
            for layer in reversed(layers):
                delta = layer.backward(delta)
        # 現在の損失を表示する。
        if i % 100 == 0:
            print(f'iter={i}, loss={layers[-1].loss/len(data)}')
        # 重み・バイアスを学習率 alpha で変化させる。
        for layer in layers:
            layer.update(alpha)
    # 結果表示。
    print('----')
    for (x,ya) in data:
        # 入力に対する出力を計算する。
        y = x
        for layer in layers:
            y = layer.forward(y)
        print(f'{int(x[0]*100)+1900}/{int(x[1]*12)+1}: days={y[0]*3+28}')

main()
