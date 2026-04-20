custom_format = (
    # TIME: Bright Yellow
    "<fg #F4D03F>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | "
    
    # LEVEL: Dynamic (Changes based on INFO, ERROR, etc.)
    "<level>{level: <8}</level> | "
    
    # PROCESS ID: Hot Pink
    "<fg #FF69B4>Proc-{process.id}</>:"
    
    # THREAD ID: Bright Orange
    "<fg #FF8C00>Thread-{thread.id}</> | "
    
    # MODULE/FILE: Lime Green
    "<fg #00FF00>{module}</>:"
    
    # FUNCTION: Bright Cyan
    "<fg #00FFFF>{function}</>:"
    
    # LINE NUMBER: Coral/Red
    "<fg #FF7F50>{line}</> - "
    
    # MESSAGE: Dynamic (Matches the level color)
    "<level>{message}</level>"
)