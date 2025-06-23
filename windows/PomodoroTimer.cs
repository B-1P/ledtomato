using System;
using System.Timers;

namespace LedTomatoWinUI
{    public enum SessionType
    {
        Work,
        ShortBreak,
        LongBreak
    }

    public enum PomodoroState
    {
        Idle = 0,
        Working = 1,
        ShortBreak = 2,
        LongBreak = 3
    }

    public class SessionCompletedEventArgs : EventArgs
    {
        public SessionType SessionType { get; }
        public int SessionNumber { get; }

        public SessionCompletedEventArgs(SessionType sessionType, int sessionNumber)
        {
            SessionType = sessionType;
            SessionNumber = sessionNumber;
        }
    }

    public class TimerStateChangedEventArgs : EventArgs
    {
        public bool IsRunning { get; }
        public SessionType CurrentSessionType { get; }

        public TimerStateChangedEventArgs(bool isRunning, SessionType currentSessionType)
        {
            IsRunning = isRunning;
            CurrentSessionType = currentSessionType;
        }
    }    public class PomodoroTimer
    {
        private Timer _timer;
        private TimeSpan _timeRemaining;
        private SessionType _currentSessionType;
        private int _completedWorkSessions;
        private bool _isRunning;
        private bool _cycleMode = false;

        public event EventHandler TimerTick;
        public event EventHandler<SessionCompletedEventArgs> SessionCompleted;
        public event EventHandler<TimerStateChangedEventArgs> StateChanged;
        public event EventHandler<SessionType> CycleAdvanced;

        public TimeSpan WorkDuration { get; set; } = TimeSpan.FromMinutes(25);
        public TimeSpan ShortBreakDuration { get; set; } = TimeSpan.FromMinutes(5);
        public TimeSpan LongBreakDuration { get; set; } = TimeSpan.FromMinutes(15);
        public int SessionsUntilLongBreak { get; set; } = 4;
        public bool AutoAdvanceBreaks { get; set; } = false;

        public TimeSpan TimeRemaining => _timeRemaining;
        public SessionType CurrentSessionType => _currentSessionType;
        public int CompletedWorkSessions => _completedWorkSessions;
        public bool IsRunning => _isRunning;
        public bool CycleMode 
        { 
            get => _cycleMode; 
            set => _cycleMode = value; 
        }

        public double Progress
        {
            get
            {
                var totalTime = GetCurrentSessionDuration();
                var elapsed = totalTime - _timeRemaining;
                return elapsed.TotalSeconds / totalTime.TotalSeconds;
            }
        }

        private TimeSpan GetCurrentSessionDuration()
        {
            return _currentSessionType switch
            {
                SessionType.Work => WorkDuration,
                SessionType.ShortBreak => ShortBreakDuration,
                SessionType.LongBreak => LongBreakDuration,
                _ => WorkDuration
            };
        }

        public PomodoroTimer()
        {
            _timer = new Timer(1000); // 1 second interval
            _timer.Elapsed += OnTimerElapsed;
            
            Reset();
        }

        public void Start()
        {
            if (!_isRunning)
            {
                _isRunning = true;
                _timer.Start();
                StateChanged?.Invoke(this, new TimerStateChangedEventArgs(_isRunning, _currentSessionType));
            }
        }

        public void Pause()
        {
            if (_isRunning)
            {
                _isRunning = false;
                _timer.Stop();
                StateChanged?.Invoke(this, new TimerStateChangedEventArgs(_isRunning, _currentSessionType));
            }
        }        public void Reset()
        {
            _timer.Stop();
            _isRunning = false;
            _currentSessionType = SessionType.Work;
            _timeRemaining = WorkDuration;
            _completedWorkSessions = 0;
            
            StateChanged?.Invoke(this, new TimerStateChangedEventArgs(_isRunning, _currentSessionType));
        }

        public void SetSessionType(SessionType sessionType)
        {
            _currentSessionType = sessionType;
            _timeRemaining = GetCurrentSessionDuration();
            StateChanged?.Invoke(this, new TimerStateChangedEventArgs(_isRunning, _currentSessionType));
        }

        private void OnTimerElapsed(object sender, ElapsedEventArgs e)
        {
            _timeRemaining = _timeRemaining.Subtract(TimeSpan.FromSeconds(1));
            
            TimerTick?.Invoke(this, EventArgs.Empty);

            if (_timeRemaining <= TimeSpan.Zero)
            {
                CompleteSession();
            }
        }

        private void CompleteSession()
        {
            _timer.Stop();
            _isRunning = false;

            SessionCompleted?.Invoke(this, new SessionCompletedEventArgs(_currentSessionType, _completedWorkSessions + 1));

            // Determine next session type
            if (_currentSessionType == SessionType.Work)
            {
                _completedWorkSessions++;
                
                // Long break after every 4 work sessions
                if (_completedWorkSessions % SessionsUntilLongBreak == 0)
                {
                    _currentSessionType = SessionType.LongBreak;
                    _timeRemaining = LongBreakDuration;
                }
                else
                {
                    _currentSessionType = SessionType.ShortBreak;
                    _timeRemaining = ShortBreakDuration;
                }
            }
            else
            {
                // After any break, go back to work
                _currentSessionType = SessionType.Work;
                _timeRemaining = WorkDuration;
            }

            StateChanged?.Invoke(this, new TimerStateChangedEventArgs(_isRunning, _currentSessionType));
        }
    }
}
