import plugins

def main():
    updater = Plugin.updater
    updater.start_polling()
    updater.idle()

if __name__ == '___main__':
    main()



