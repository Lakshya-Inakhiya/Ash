# Ash Robot - Intelligent Gestures 🤖

Ash now automatically chooses gestures based on what you say!

## 🧠 How It Works

Ash analyzes your words and picks appropriate gestures:

### 🙋 Greetings → WAVE
**Trigger words:** hello, hi, hey, greet, wave, say hello, say hi

**Examples:**
```
You: Hello Ash!
→ Ash waves while saying hello

You: Greet Sunil sir
→ Ash waves while greeting Sunil

You: Say hi to everyone
→ Ash waves while saying hi
```

### 🎉 Celebrations → ARMS UP
**Trigger words:** yay, awesome, great, celebrate, congratulations, congrats, 
                  hooray, excellent, amazing, fantastic

**Examples:**
```
You: That's awesome!
→ Ash raises arms up while responding

You: Congratulations on your achievement
→ Ash raises arms up to celebrate
```

### 👉 Questions → POINT (Explaining)
**Trigger words:** what, why, how, when, where, who, explain, tell me, ?

**Examples:**
```
You: What is the capital of France?
→ Ash points while explaining

You: How does gravity work?
→ Ash points while explaining

You: Tell me about robots
→ Ash points while explaining
```

### 🤷 Everything Else → DEFAULT FLOW
- Thinking: Point
- Speaking: (current gesture)
- Happy: Arms Up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 💡 Example Interactions

### Example 1: Simple Greeting
```
You: Hello!
[Thinking...]
[Gesture: Wave]          ← Ash waves!
Ash: Hello! How can I help you today?
```

### Example 2: Greeting Someone
```
You: Greet Sunil sir
[Thinking...]
[Gesture: Wave]          ← Ash waves while greeting!
Ash: Hello Sunil Sir! It's a pleasure to meet you.
```

### Example 3: Asking a Question
```
You: What is 2 + 2?
[Thinking...]
[Gesture: Point]         ← Ash points while explaining!
Ash: The answer is 4.
```

### Example 4: Celebrating
```
You: That's amazing!
[Thinking...]
[Gesture: Arms Up]       ← Ash celebrates with you!
Ash: I'm glad you think so!
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🎭 Gesture Priority

When multiple keywords match:
1. Greetings (Wave) - highest priority
2. Celebrations (Arms Up)
3. Questions (Point)
4. Default (Point → Arms Up)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🧪 Try These Examples:

In Ash conversation, type:

```
You: Hello Ash, who are you?
→ Waves because "hello" detected (greeting priority)

You: Greet my friend
→ Waves because "greet" detected

You: What is your name?
→ Points because "what" detected

You: That's fantastic!
→ Arms up because "fantastic" detected

You: Tell me a joke
→ Points because "tell me" detected
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🎯 Watch Both:

1. **Console**: Shows `[Gesture: Wave]` or `[Gesture: Point]`
2. **Face Window**: Changes expressions to match
3. **Servo Output**: Shows arm positions (simulation on Mac)

On the Raspberry Pi with real servos, you'll see actual arm movements!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ✨ Smart Gestures Active!

Ash is now context-aware and will gesture naturally! 🤖
