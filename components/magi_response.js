import React from 'react';
const $ = React.createElement;

// MAGI-UI's version of upstream's components/response.js (which is not modified):
// the same panel, colors and flicker, with labels that match the skill's
// resolution. 可決 / 否決 (passed / rejected) instead of 合意 / 拒絶, since a
// 2/3 pass is not an agreement; 異常 instead of 誤差 for a failed unit.
function getStatusText(status) {
    if (status === 'info')
        return '情 報';

    if (status === 'yes')
        return '可 決';

    if (status === 'no')
        return '否 決';

    if (status === 'conditional')
        return '状 態';

    if (status === 'error')
        return '異 常';

    throw new Error('Invalid status: ' + status);
}

function getStatusColor(status) {
    if (status === 'info')
        return '#3caee0';

    if (status === 'yes')
        return '#52e691';

    if (status === 'no')
        return '#a41413';

    if (status === 'conditional')
        return '#ff8d00';

    if (status === 'error')
        return 'gray';

    throw new Error('Invalid status: ' + status);
}

export default function MagiResponse({ status, question_id, answer_id }) {
    const text = getStatusText(status);
    const color = getStatusColor(status);

    let className = 'response';
    if (question_id !== answer_id)
        className += ' flicker';

    return $('div', { className, style: { color: color, borderColor: color } },
        $('div', { className: 'inner' }, text)
    );
}

MagiResponse.defaultProps = {
    status: 'info',
    question_id: 0,
    answer_id: 0
};
