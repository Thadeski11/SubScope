import argparse
import socket
import time
import asyncio
import dns.asyncresolver

parser = argparse.ArgumentParser(prog="SubScope", description="")
parser.add_argument("-d", "--domain", help="Passar o domínio alvo.")
parser.add_argument("-w", "--wordlist", help="Passar a payload de testes.")
parser.add_argument("-t", "--time", type=int, default=10, help="Definir tempo limite por segundo")
parser.add_argument("-o", "--output", help="Salva os resultados em um arquivo de texto.")
args = parser.parse_args()


async def DNS(subdomain, semaphore):
	async with semaphore:
		try:
			loop = asyncio.get_running_loop()
			dados = await loop.run_in_executor(None, socket.getaddrinfo, subdomain, None, socket.AF_INET)
			addr = dados[2][4][0]
			return subdomain, addr
		except (socket.gaierror, UnicodeError):
			return subdomain, None

async def Main(domain, wordlist, timed=10):
	semaphore = asyncio.Semaphore(timed)

	subdomains = []
	subdomains_done = []

	with open(wordlist, "r") as f:
		for i in f:
			i = i.strip()
			subdomain_test = f"{i}.{domain}"
			subdomains.append(subdomain_test)

	addr = [DNS(subdomain, semaphore) for subdomain in subdomains]
	tasks_done = await asyncio.gather(*addr)
	for subdomain, ip in tasks_done:
		if ip:
			subdomains_done.append(subdomain)

	return subdomains_done


def Output(results, file_name):
	if file_name:
		if isinstance(results, list):
			with open(f"{file_name}", "w") as f:
				for i in results:
					f.write(i + "\n")


async def run_check_subdomain():
	results_subdomains = await Main(args.domain, args.wordlist, args.time)
	for alive in results_subdomains:
		print(alive)
	return results_subdomains

results_subdomains = asyncio.run(run_check_subdomain())
Output(results_subdomains, args.output)
