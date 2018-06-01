class Config:
    enable_utc = True
    timezone = 'Asia/Shanghai'
    file_server = '/var/mlcc/server'
    task_routes = {
        'mlcc.worker.*': {
            'queue': 'server'
        },
        'mlcc.node.worker.*': {
            'queue': 'node'
        }
    }
