import React, { useState } from 'react';
import './ReferenceApp.css';
import Modal from './Modal';

const categories = [
  'Network', 'Software', 'Training', 'Email', 'Consulting', 'Support',
  'Database', 'Hardware', 'Printer', 'Security', 'VPN', 'Access',
  'Website', 'Development', 'SAP', 'Network/security'
];

const ReferenceApp = () => {
  const [category, setCategory] = useState('');
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [similarQueries, setSimilarQueries] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [selectedSolution, setSelectedSolution] = useState('');
  const [alternativeResponse, setAlternativeResponse] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleInputChange = (e) => {
    const value = e.target.value;
    const englishOnly = value.replace(/[^a-zA-Z0-9\s.,?!]/g, ''); 
    setQuery(englishOnly);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      alert("Пожалуйста, введите запрос.");
      return;
    }
    setLoading(true);
    setResponse('');
    setSimilarQueries([]);
    setAlternativeResponse(null);

    try {
      const res = await fetch('http://localhost:4000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category,
          query,
        }),
      });

      const data = await res.json();
      setResponse(data.answer);

      const queriesWithSolutions = data.similar_queries.map((question) => ({
        question,
        solution: data.exact_answer_map[question] || 'Ответ не найден.'
      }));

      setSimilarQueries(queriesWithSolutions);
    } catch (error) {
      console.error('Ошибка при отправке запроса:', error);
      setResponse('Произошла ошибка. Попробуйте снова.');
    }

    setLoading(false);
  };

  const handleAlternativeSearch = async () => {
    setLoading(true);
    setAlternativeResponse(null);

    try {
      const res = await fetch('http://localhost:4000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category,
          query,
          alternative: true,
        }),
      });

      const data = await res.json();
      setAlternativeResponse(data.answer);
    } catch (error) {
      console.error('Ошибка при получении альтернативного ответа:', error);
      setAlternativeResponse('Произошла ошибка. Попробуйте снова.');
    }

    setLoading(false);
  };

  const handleQuestionClick = (question, solution) => {
    setSelectedQuestion(question);
    setSelectedSolution(solution);
  };

  const closeModal = () => {
    setSelectedQuestion(null);
    setSelectedSolution('');
    setIsModalOpen(false);
  };

  function cleanText(text) {
    return text.replace(/[^\x00-\x7F]/g, "");
  }

  return (
    <div className="app-container">
      <div className="left-panel">
        <div className='header'>
          <div className='header-logo-container'>
            <img className='header-logo' src={require('../src/icons/chat-image.png')} />
          </div>
          <h3 className='header-title'>САМО - ваш виртуальный помощник</h3>
        </div>
        <form onSubmit={handleSubmit}>
          <label>Запрос</label>
          <input
            type="text"
            placeholder="Введите запрос"
            value={query}
            onChange={handleInputChange}
            required
          />
          
          <button type="submit">Анализировать</button>
        </form>
      </div>

      <div className="right-panel">
        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : (
          <div className="response">
            <button className='response-close-modal-button' onClick={() => setIsModalOpen(true)}>
              <img className='response-close-modal' src={require('../src/icons/folder-open.png')} />
            </button>
            <h4>Ответ:</h4>
            <pre className='response-text'>{cleanText(response) || 'Ответ будет отображен здесь.'}</pre>
            {response && (
              <button className='response-button' onClick={handleAlternativeSearch}>Найти другой ответ</button>
            )}
          </div>
        )}

        {alternativeResponse && (
          <div className="alternative-response">
            <button className='response-close-modal-button' onClick={() => setIsModalOpen(true)}>
              <img className='response-close-modal' src={require('../src/icons/folder-open.png')} />
            </button>
            <h4>Альтернативный ответ:</h4>
            <pre className='response-text'>{cleanText(alternativeResponse)}</pre>
          </div>
        )}

        {similarQueries.length > 0 && (
          <div className="similar-queries">
            <h3>Похожие вопросы:</h3>
            <ul>
              {similarQueries.map((item, index) => (
                <li key={index} onClick={() => handleQuestionClick(item.question, item.solution)}>
                  {item.question}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {isModalOpen && (
        <Modal question="Ответ" solution={cleanText(response)} onClose={closeModal} />
      )}

      {selectedQuestion && (
        <Modal question={selectedQuestion} solution={selectedSolution} onClose={closeModal} />
      )}
    </div>
  );
};

export default ReferenceApp;
