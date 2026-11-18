import React from 'react';
const $ = React.createElement;

// MAGI-UI's version of upstream's components/status.js (which is not modified):
// the same five lines and class names, with CODE, EXTENTION and PRIORITY taken
// from the result (ai.status_fields). FILE and EX_MODE stay as upstream shows them.
export default function MagiStatus({ code, extention, priority }) {
    return $('div', { className: 'system-status' },
        $('div', {}, `CODE:${code}`),
        $('div', {}, 'FILE:MAGI_SYS'),
        $('div', {}, `EXTENTION:${extention}`),
        $('div', {}, 'EX_MODE:OFF'),
        $('div', {}, `PRIORITY:${priority}`)
    );
}

MagiStatus.defaultProps = {
    code: '473',
    extention: '????',
    priority: 'AAA'
};
