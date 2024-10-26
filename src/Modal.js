import React from 'react';
import './Modal.css';

function Modal({ question, solution, onClose }) {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
      <button className='response-close-modal-button' onClick={onClose}>
        <img className='response-close-modal' src={require('../src/icons/cross.png')} />
      </button>
        <h2 className='modal-title'>Вопрос: {question}</h2>
        <p className='modal-solution'>{solution}</p> {}
        <button className='modal-button' onClick={onClose}>Закрыть</button>
      </div>
    </div>
  );
}

export default Modal;
