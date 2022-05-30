import random
answer = random.randint(1,100)
###aaaaa
number = int(input('数字を当ててみてね！'))

while answer != number:
    if answer > number:
        print('はずれ！もっと大きい数字だよ？ｗｗｗ')
    if answer < number:
        print('はずれ！もっと小さい数字だよ？www')

    number = int(input('数字を当ててみてね！'))
print("ブラボー！正解です！")
