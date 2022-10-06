import os

num = 21
os.chdir("./bin")
while num < 42:
    os.system(f"python gaps --image=target_{num}.jpg   --save  --verbose  --size=80")
    num += 1