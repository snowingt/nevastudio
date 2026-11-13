import React, { useState } from 'react'

export type WizardStep = 1 | 2 | 3

interface Props {
  currentStep?: WizardStep
  onStepChange?: (step: WizardStep) => void
  styleTitle?: string
  estimatedTime?: string
  onComplete?: () => void
}

export function StudioWizard({
  currentStep = 1,
  onStepChange,
  styleTitle = 'Estudio de Edición Dinámica',
  estimatedTime = '~2–3 min (Gama Media 12GB)',
  onComplete
}: Props) {
  const [step, setStep] = useState<WizardStep>(currentStep)

  const goTo = (s: WizardStep) => {
    setStep(s)
    onStepChange?.(s)
  }

  return (
    <div className="wizard-container">
      <div className="wizard-steps-header">
        <button
          type="button"
          className={`wizard-step-tab ${step === 1 ? 'active' : ''} ${step > 1 ? 'completed' : ''}`}
          onClick={() => goTo(1)}
        >
          <div className="wizard-step-num">{step > 1 ? '✓' : '1'}</div>
          <div>
            <div className="wizard-step-title">1. Idea & Guion</div>
            <div className="wizard-step-sub">Estructura y gancho viral</div>
          </div>
        </button>

        <span className="wizard-arrow">→</span>

        <button
          type="button"
          className={`wizard-step-tab ${step === 2 ? 'active' : ''} ${step > 2 ? 'completed' : ''}`}
          onClick={() => goTo(2)}
        >
          <div className="wizard-step-num">{step > 2 ? '✓' : '2'}</div>
          <div>
            <div className="wizard-step-title">2. Voz & Escenas</div>
            <div className="wizard-step-sub">TTS rápido / Clonada & B-roll</div>
          </div>
        </button>

        <span className="wizard-arrow">→</span>

        <button
          type="button"
          className={`wizard-step-tab ${step === 3 ? 'active' : ''}`}
          onClick={() => goTo(3)}
        >
          <div className="wizard-step-num">3</div>
          <div>
            <div className="wizard-step-title">3. Render & Publicación</div>
            <div className="wizard-step-sub">{estimatedTime}</div>
          </div>
        </button>
      </div>
    </div>
  )
}
