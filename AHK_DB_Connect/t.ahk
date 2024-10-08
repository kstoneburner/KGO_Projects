#Include AHKsock.ahk

    ;Register OnExit subroutine so that AHKsock_Close is called before exit
    ;OnExit, CloseAHKsock
    
    ;Add menu item for exiting gracefully (see comment block in CloseAHKsock)
    ;Menu, Tray, Add
    ;Menu, Tray, Add, Exit Gracefully, CloseAHKsock
    
    ;Set up an error handler (this is optional)
    AHKsock_ErrorHandler("AHKsockErrors")
    
    ;Create the binary data which will be sent to any client that connects.
    ;It is just an example; you can change it if you want.
    VarSetCapacity(bData, bDataLength := 10, 0xFF)

    ;Listen on port 27015
    If (i := AHKsock_Listen(27015, "Send")) {
        OutputDebug, % "AHKsock_Listen() failed with return value = " i " and ErrorLevel = " ErrorLevel
        ExitApp
    }
response(input){
    msgbox DING `n %input%
}

