cp = ''
hw = ''
uid = ''
mac = ''
sw = ''
with open('/boot_out.txt') as f:
    content = f.read().split()
    cp = content[2]
    hw = next((x for x in content if 'ID' in x))[3:]
    uid = next((x for x in content if 'UID' in x))[4:]
    mac = next((x for x in content if 'MAC' in x))[4:]
    sw = next((x for x in content if 'SW' in x))[3:]
