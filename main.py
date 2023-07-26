import os
import questionary as qy

import detect_uid
import signup

def main():
    
    while True:
        try:
            os.system('clear')
            opt = qy.select('Mode', choices=[
                qy.Choice(title='Door Control', value=0),
                qy.Choice(title='User Manager', value=1),
                qy.Separator('----'),
                qy.Choice(title='Exit *', value=-1),
            ]).ask()
            
            if opt == -1:
                break
            elif opt == 0:
                detect_uid.main()
            elif opt == 1:
                signup.main()
                
        except KeyboardInterrupt:
            break
        
    print('Bye!')
    return True

if __name__ == '__main__':
    detect_uid.main()
    main()