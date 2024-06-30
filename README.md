This is a personal and a simple learning project with base for controlling any os with natural touch/air gestures.
Target: Perforamce focused, dual process and multi threaded communication between modues using queues, while minimising IPC and improving UEP.

Os: this is targetted to be os independant (current is tested for linux and windows....Mac darwin hads some issues for now (minor bugs to be fixed)

for UI it uses feature rich Pyqt5.....may move to more perf efficent enlightenment based or Gnome based libraries for faster IPC

Current Structure: 
Two processes are forked. 
P1 runs recognition pipeline with OCR and device in sperate threads. 
P2 maintains UI life cycle (with independent UI module....(needs to switchable with other UI loops))
OCR thread does IPC with P2.
















