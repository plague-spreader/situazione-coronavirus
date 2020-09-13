#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import requests
import tabulate
import datetime
import pathlib

csv_nazionale = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/\
dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
csv_regionale = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/\
dati-regioni/dpc-covid19-ita-regioni.csv"
regioni = {\
0:"Nazionale",\
1:"Piemonte",\
2:"Valle d'Aosta",\
3:"Lombardia",\
5:"Veneto",\
6:"Friuli Venezia Giulia",\
7:"Liguria",\
8:"Emilia-Romagna",\
9:"Toscana",\
10:"Umbria",\
11:"Marche",\
12:"Lazio",\
13:"Abruzzo",\
14:"Molise",\
15:"Campania",\
16:"Puglia",\
17:"Basilicata",\
18:"Calabria",\
19:"Sicilia",\
20:"Sardegna",\
21:"P.A. Bolzano",\
22:"P.A. Trento"\
}

def read_csv(csv_url, local):
	if local:
		path = pathlib.Path(csv_url)
		if not path.is_file():
			return None
		with path.open() as f:
			lines = f.readlines()
	else:
		lines = requests.get(csv_url).text
		lines = lines.split("\n")
	
	headers = lines[0].split(",")
	num_cols = len(headers)
	lines = lines[1:]
	csv_content = []
	for line in lines:
		comma_separated = line.split(",")
		if len(comma_separated) < num_cols:
			continue
		tmp = []
		tmp.extend(comma_separated[:num_cols-1])
		tmp.append(",".join(comma_separated[num_cols-1:]))
		csv_content.append(tuple(tmp))
	return (headers, csv_content)

def divs(data):
	ret = []
	for (n, d) in zip(data[1:], data[:-1]):
		if d != 0:
			ret.append(n/d)
		else:
			ret.append(0)
	return ret

def slice2iter(sl):
	return range(sl.start, sl.stop)

def show_data1(dates, values):
	up = True
	old = values[0]
	diff = [old]
	for v in values[1:]:
		diff.append(v - old)
		old = v
	mean_diff = sum(map(abs, diff))/len(diff)
	growth = []
	for i in range(1, len(diff)):
		growth.append(float("inf") if diff[i-1] == 0 else diff[i]/diff[i-1])
	plt.xticks(range(len(values)), dates, rotation="vertical", fontsize=6)
	for i in range(len(values)):
		v = values[i]
		plt.plot([i, i], [min(values), v], ":k")
		k = i - 1
		if k >= 0:
			g = growth[k]
			mod = abs(g)
			if g < 0:
				up = not up
			if mod != 0 and mod != float("inf"):
				direction = 0.3 * mean_diff
				if up:
					s = "r-^"
				else:
					s = "g-v"
					direction *= -1
				plt.plot([i, i], [v, v + direction * mod], s)
	
	print(tabulate.tabulate(zip(dates, values, [None, *growth]), \
headers=("Data", "Numero positivi", "Fattore di crescita")))
	
	plt.plot(values, "b-*")
	plt.title("Last date: {}".format(dates[-1]))
	plt.show()

def show_data(dates, values):
	# TODO devo fare la divisione fra le differenze
	# \frac{{\DeltaN}_d}{{\DeltaN}_{d-1}}
	fracs = divs(values)
	accel = divs(fracs)
	print(tabulate.tabulate(\
zip(dates, values, [None, *fracs], [None, None, *accel]), \
headers=("Data", "Numero positivi", "Velocita'", "Accelerazione")))
	plt.fill_between([0, len(accel)], min(accel), 1, color=[0,1,0,0.4])
	plt.fill_between([0, len(accel)], 1, max(accel), color=[1,0,0,0.4])
	plt.xticks(range(len(accel)), dates[2:], rotation="vertical", fontsize=6)
	for i in range(len(accel)):
		plt.plot([i, i], [min(accel), accel[i]], ":k")
	plt.plot(accel, "b-*")
	plt.title("Last date: {}".format(dates[-1]))
	plt.show()
	plt.fill_between([0, len(fracs)], min(fracs), 1, color=[0,1,0,0.4])
	plt.fill_between([0, len(fracs)], 1, max(fracs), color=[1,0,0,0.4])
	plt.xticks(range(len(fracs)), dates[1:], rotation="vertical", fontsize=6)
	for i in range(len(fracs)):
		plt.plot([i, i], [min(fracs), fracs[i]], ":k")
	plt.plot(fracs, "b-*")
	plt.title("Last date: {}".format(dates[-1]))
	plt.show()
	if fracs[-1] > 1:
		color = [1,0,0,0.4]
	elif fracs[-1] < 1:
		color = [0,1,0,0.4]
	else:
		color = [1,1,0,0.4]
	plt.fill_between([0, len(values)], min(values), max(values), color=color)
	plt.xticks(range(len(values)), dates, rotation="vertical", fontsize=6)
	for i in range(len(values)):
		plt.plot([i, i], [min(values), values[i]], ":k")
	plt.plot(values, "b-*")
	plt.title("Last date: {}".format(dates[-1]))
	plt.show()

def show_data_and_means(dates, values):
	(weekly_dates, weekly_values) = to_weekly(dates, values)
	len_values = len(values)
	x_means = []
	y_means = []
	i1 = iter(weekly_values)
	for i in range(0, len_values, 7):
		me = next(i1)
		k = min(7, len_values - i)
		# x_means.append(i + min(k, 3))
		# y_means.append(me)
		sl = slice(i, i+k)
		V = values[sl]
		plt.plot(slice2iter(sl), V, 'k:.')
		mv = min(V)
		Mv = max(V)
		g_me = (mv + Mv)/2
		plt.plot([i, i, i+k, i+k, i], [Mv, mv, mv, Mv, Mv], 'b-*')
		if me < g_me:
			s = "r-v"
		if me > g_me:
			s = "r-^"
		plt.plot([i, i], [me, g_me], s)
		plt.plot([i+k, i+k], [me, g_me], s)
		plt.plot([i, i+k], [me, me], 'r-')
		plt.plot([i, i+k], [g_me, g_me], 'g-')
		# plt.plot([i, i], [me, g_me], 'g-')
		# plt.plot([i+k, i+k], [me, g_me], 'g-')
	plt.show()

def get_k_days(date, k=7):
	k_days = date + datetime.timedelta(days=k)
	return "{:02d}/{:02d} - {:02d}/{:02d}".format(date.day, date.month, \
k_days.day, k_days.month)

def mean_k_days(values):
	return sum(values)/len(values)

def to_weekly(dates, values):
	(weekly_dates, weekly_values) = ([], [])
	l = len(dates)
	for i in range(0, l, 7):
		k = min(7, l-i)
		weekly_dates.append(get_k_days(dates[i], k=k-1))
		weekly_values.append(mean_k_days(values[i:i+k]))
	return (weekly_dates, weekly_values)

def save_tmp_file(tmp_filename, headers, data):
	with open(tmp_filename, "w") as f:
		f.write(",".join(headers))
		f.write("\n")
		for line in data:
			f.write(",".join(line))
			f.write("\n")

def parse_csv_nazionale(headers, data):
	(dates, values) = ([], [])
	for x in data:
		dates.append(datetime.datetime.fromisoformat(x[0]))
		values.append(float(x[6]))
		# values.append(float(x[7]))
	return (dates, values)

def parse_csv_regionale(headers, data, codice_regionale):
	(dates, values) = ([], [])
	for x in data:
		if int(x[2]) == codice_regionale:
			dates.append(datetime.datetime.fromisoformat(x[0]))
			values.append(float(x[10]))
			# values.append(float(x[11]))
	return (dates, values)

def get_csv_data(codice_regionale):
	if codice_regionale == 0:
		tmp_filename = "/tmp/csv_nazionale"
		url = csv_nazionale
		parse = parse_csv_nazionale
	else:
		tmp_filename = "/tmp/csv_regionale"
		url = csv_regionale
		parse = lambda h, d: parse_csv_regionale(h, d, codice_regionale)
	
	ret = read_csv(tmp_filename, True)
	downloaded = False
	if ret == None:
		(headers, data) = read_csv(url, False)
		save_tmp_file(tmp_filename, headers, data)
		downloaded = True
	else:
		(headers, data) = ret
	(dates, values) = parse(headers, data)
	now = datetime.datetime.now()
	acceptable_day = now.day
	if now.hour < 17:
		acceptable_day -= 1
	if dates[-1].day != acceptable_day and not downloaded:
		(headers, data) = read_csv(url, False)
		save_tmp_file(tmp_filename, headers, data)
		(dates, values) = parse(headers, data)
	return (dates, values)

def main(args):
	for reg_code in args.reg_codes:
		if reg_code == 0:
			print("Dati nazionali:")
		else:
			print("Dati regione {}:".format(regioni[reg_code]))
		(dates, values) = get_csv_data(reg_code)
		# show_data(*to_weekly(dates, values))
		show_data1(*to_weekly(dates, values))
		# show_data_and_means(dates, values)
		print()

def parse_reg_codes(x):
	x = int(x)
	if x not in regioni:
		raise argparse.ArgumentTypeError("Incorrect code \"{}\"".format(x))
	return x

def get_help_reg_codes():
	ret = ["Formato (codice, regione):"]
	for (codice, regione) in regioni.items():
		ret.append("({}, {})".format(codice, regione))
	return "\n".join(ret)

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("reg_codes", nargs="+", type=parse_reg_codes, \
help=get_help_reg_codes())
	main(ap.parse_args())
