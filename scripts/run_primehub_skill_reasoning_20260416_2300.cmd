@echo off
setlocal
cd /d "C:\projects\Hermes Skills"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\projects\Hermes Skills\scripts\start_primehub_skill_reasoning_batch.ps1" -RunId "primehub-skill-reasoning-20260416-2100mdt" -RunRoot "C:\projects\Hermes Skills\data\primehub_skill_reasoning_batch_20260416_2100mdt"
