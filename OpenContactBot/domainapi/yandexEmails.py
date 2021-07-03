def buildYandexAliasList(emailInTicket):
    """ Yandex use many alias for own mail, it`s same email.
    We need search all alias in system """

    cnameYandexMail = [
            'yandex.ru',
            'yandex.ua',
            'yandex.by',
            'yandex.kz',
            'yandex.com',
            'ya.ru'
    ]

    aliasListEmailFromTicket = []

    if(emailInTicket.split('@')[1] in cnameYandexMail):
        usernameEmail = emailInTicket.split('@')[0]
            
        for yaAlias in cnameYandexMail:
             aliasListEmailFromTicket.append('%s@%s'%(usernameEmail,yaAlias))
    else:
        aliasListEmailFromTicket.append(emailInTicket)

    return aliasListEmailFromTicket
