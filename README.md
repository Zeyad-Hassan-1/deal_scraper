# Zezo's Deal Scraper 🚀

This is an automated web scraper and Telegram bot that helps you find the best Laptop deals across major Egyptian e-commerce platforms like Jumia and 2B!

You can interact with the bot directly on Telegram here: 
**[Zezo Deals Bot (@zezo_deals_bot)](https://web.telegram.org/k/#@zezo_deals_bot)**

## Architecture
- **Scraping Engine**: Scrapy (Python)
- **Data Processing**: Pandas scripts for cleaning and filtering (RAM, Hard Disk, GPU, Price, etc.)
- **Orchestration**: n8n workflows
- **Proxy**: Cloudflare WARP via local SOCKS5 proxy to bypass WAFs (like Cloudflare blocks)
- **Deployment**: Docker Compose on Azure VM, exposed to the web via Cloudflare Tunnels

## How to Deploy
1. **Clone the Repo** on your server.
2. **Setup Cloudflare WARP**:
   Install `cloudflare-warp` on your server and configure it as a proxy:
   ```bash
   warp-cli --accept-tos registration new
   warp-cli --accept-tos mode proxy
   warp-cli --accept-tos proxy port 40000
   warp-cli --accept-tos connect
   ```
3. **Configure the Environment**:
   ```bash
   echo 'PROXY_URL=socks5://172.17.0.1:40000' > .env
   ```
4. **Deploy with Docker**:
   ```bash
   cd Egy_stores_azure
   sudo docker-compose up -d --build
   ```
5. **Start Cloudflare Tunnel** for n8n:
   ```bash
   nohup ./cloudflared-linux-amd64 tunnel --url http://localhost:5678 > cloudflared.log 2>&1 &
   ```
   Check `cloudflared.log` to get the public URL for n8n.

## Usage
Simply type `/start` in the Telegram Bot and follow the prompts! The bot will ask for your preferences (RAM, Hard Disk, GPU, Budget) and automatically kick off the spiders, clean the data, filter the results, and return the best deals to you.
