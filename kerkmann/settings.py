# Scrapy settings for kerkmann project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'kerkmann'

# Это список модулей, содержащих пауков, которые Scrapy будет искать. Значение по умолчанию: []
SPIDER_MODULES = ['kerkmann.spiders']
# Это модуль, в котором новый паук создается с помощью команды genspider. Значение по умолчанию: »
NEWSPIDER_MODULE = 'kerkmann.spiders'

# Он определяет пользовательский агент, который будет использоваться при сканировании сайта.
# Значение по умолчанию: «Scrapy / VERSION (+ http: //scrapy.org)»
#USER_AGENT = 'ebay (+http://www.yourdomain.com)'

# Scrapy соблюдает правила robots.txt, если установлено значение true
ROBOTSTXT_OBEY = False

# Максимальное количество существующих запросов, которые выполняет загрузчик Scrapy (default: 16) (було - 3)
CONCURRENT_REQUESTS = 1       # 3

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs

# Он определяет общее время загрузки до загрузки страниц с сайта (default-0)  задержк между двумя скачиваниями
DOWNLOAD_DELAY = 1         # 0.125
# Максимальное количество существующих запросов, которые выполняются одновременно для любого отдельного домена (default -8)
CONCURRENT_REQUESTS_PER_DOMAIN = 1   # 32
# Максимальное количество существующих запросов, выполняемых одновременно к любому отдельному IP.(default -0)
CONCURRENT_REQUESTS_PER_IP = 1   #16

# По умолчанию в Scrapy используются файлы cookie (enabled by default) ???
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ebay.middlewares.EbaySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'ebay.middlewares.EbayDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'ebay.pipelines.EbayPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html


# а регулирует загрузку. (задержка в зависимости от времени ответа сервера) (default- False)
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

LOG_LEVEL = 'ERROR'
#-------------------------------- змінено
HTTPERROR_ALLOW_ALL = True
#HTTPERROR_ALLOWED_CODES = [404,403]
# Исправляет символы Unicode !!!
FEED_EXPORT_ENCODING = 'utf-8'

