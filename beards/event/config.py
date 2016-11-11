class Config:
    '''
    set the commands for managing events, and the configurations for each event.
    Each event configuration is a dictionary in the events Config.events list.

    event_name: What skybeard will call the event in the chat
    init_kwd: How users specify the event to skybeard, (e.g /event <init_kwd>)
    max_people: How many people can participate
    warn_time: How long before the event skybeard should send a reminder (in minutes)
    '''

    #global event config
    new_evt_kwd = 'event'
    del_evt_kwd = 'delevent'
    list_evt_kwd = 'events'
    
    #command to reserve a place
    res_kwd = 'shotgun'
    #command to unreserve a place
    unres_kwd =  'unshotgun'

    #command to decare readiness
    rdy_kwd = 'rdry'

    #command to undeclare readiness
    unrdy_kwd = 'unrdry'

    #add configurations for new events here:
    events = [
            dict(
                event_name = 'Overwatch',
                init_kwd = 'overwatch',
                max_people = 6,
                warn_time = 5
                ),
            dict(
                event_name = 'Dota 2',
                init_kwd = 'dota',
                max_people = 5,
                warn_time = 5
                ),
            dict(
                event_name = 'Fractured Space',
                init_kwd = 'spotes',
                max_people = 5,
                warn_time = 5
                ),
            dict(
                event_name = 'World of Warships',
                init_kwd = 'botes',
                max_people = 3,
                warn_time = 5
                ),
            ]


