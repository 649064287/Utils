import bisect

def find_nearest_loss(freg, freq_loss_data):
    freq_values = [freq for freq, _ in freq_loss_data]
    index = bisect.bisect_left(freq_values, freg)

    if index == 0:
        return round(freq_loss_data[0][1], 1)
    elif index == len(freq_values):
        return round(freq_loss_data[-1][1], 1)
    else:
        freq1, loss1 = freq_loss_data[index - 1]
        freq2, loss2 = freq_loss_data[index]
        if abs(freq1 - freg) <= abs(freq2 - freg):
            return round(loss1, 1)
        else:
            return round(loss2, 1)

# 输入第一组数据
freg = int(input())
# 输入第二组数据
freq_loss_data = []
data = input().split(",")
for item in data:
    freq, loss = item.split(":")
    freq_loss_data.append((int(freq), int(loss)))

result = find_nearest_loss(freg, freq_loss_data)
print(result)