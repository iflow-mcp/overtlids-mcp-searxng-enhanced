def run_sync():
    """Synchronous entry point for console_scripts"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, exiting.")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Fatal error starting server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_sync()